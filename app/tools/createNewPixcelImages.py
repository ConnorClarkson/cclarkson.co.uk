import os
import ssl
import urllib.request
from html.parser import HTMLParser

import cv2
import math
import requests
# from app import settings
from lxml import html


class grabChildPages(HTMLParser):
    htmlList = []

    def handle_starttag(self, tag, attrs):
        for attr in attrs:
            if attr[0] == 'href' and not attr[1] == None:
                if "/species/" in attr[1] and attr[1] not in self.htmlList \
                        and not "https://" in attr[1] and not "?" in attr[1]:
                    self.htmlList.append("http://www.worldwildlife.org" + attr[1])


def grabImages(childpage):
    tree = html.fromstring(childpage.content)
    img = tree.xpath('//div/@data-src')
    for i in img:
        if '/story_full_width/' in i or '/hero_full/' in i:
            return i

    for i in img:
        if 'hero_small' in i or 'portrait_overview' in i:
            return i


def grabDetails(childpage):
    tree = html.fromstring(childpage.content)
    details = {}
    population = tree.xpath('//strong[@class="hdr"]')
    for p in population:
        sibling = p.getnext()
        if sibling is not None:
            title = sibling.getprevious().text
            if title not in ['Status', 'Population', 'Scientific Name', 'Height', 'Weight', 'Habitats', 'Places']:
                continue
            if sibling.text.strip() == "":
                for elem in sibling.getchildren():
                    if elem.text.strip() != "":
                        if title in details:
                            details[title] = details[title] + ", " + elem.text.strip()
                        else:
                            txt = elem.text.strip()
                            txt = txt[0].upper() + txt[1:]
                            details[title] = txt
            if sibling.text.strip() != "":
                if title in details:
                    details[title] = details[title] + ", " + sibling.text.strip()
                else:
                    txt = sibling.text.strip()
                    txt = txt[0].upper() + txt[1:]
                    details[title] = txt
    tmp = []
    for key in details:
        tmp.append([key, details[key]])
    return tmp


def calculate_population(animal):
    pop_text = animal[1][1][1]
    text = pop_text.split(' ')
    nums = []
    for word in text:
        splitvar = '-'
        if '–' in word:
            splitvar = '–'
        elif '–' in word:
            splitvar = '–'
        elif '–' in word:
            splitvar = '–'

        for subsplit in word.split(splitvar):
            try:
                num = float(subsplit.replace(',', ''))
                if num not in nums:
                    nums.append(num)
            except ValueError as e:
                pass
    if not nums:
        if 'Unknown' in pop_text:
            nums = ['Unknown']
        elif 'extinct' in pop_text:
            nums = ['Extinct']
        else:
            nums = ['Unknown']
        return nums

    if len(nums) == 1:
        nums = [nums[0], nums[0]]
    if len(nums) > 2:
        nums = [nums[0], nums[0]]
    return nums


if __name__ == "__main__":
    url = 'http://www.worldwildlife.org/species/directory?direction=desc&sort=extinction_status'
    ROOT = "../static/img/WWF"  # os.path.join(settings.APP_STATIC, "img/WWF")
    response = urllib.request.urlopen(url, context=ssl._create_unverified_context())
    webContent = response.read()
    parser = grabChildPages()
    parser.feed(webContent.decode("utf-8"))
    webpageList = parser.htmlList[2:]
    imgHTMLList = []
    for page in webpageList:
        response = requests.get(page)
        details = grabDetails(response)
        if 'Endangered' in details[0][1]:
            image = grabImages(response)
            filename = page.split('/')[-1]
            filename = filename.replace('-', '_')
            imgHTMLList.append([page, details, image, filename, "{}/animalImages/{}.jpg".format(ROOT, filename)])

    for filename in os.listdir(ROOT + '/animalImages/'):
        os.remove(ROOT + '/animalImages/' + filename)
    for filename in os.listdir(ROOT + '/resizedImages/'):
        os.remove(ROOT + '/resizedImages/' + filename)
    for filename in os.listdir(ROOT + '/outputImages/'):
        os.remove(ROOT + '/outputImages/' + filename)
    for imageUrl in imgHTMLList:
        if imageUrl[2] != "":
            try:
                urllib.request.urlretrieve(str(imageUrl[2]), imageUrl[-1])
            except:
                print(imageUrl[-1])
    final_csv = []
    for animal in imgHTMLList:
        numList = calculate_population(animal)
        if numList is not None:
            if not os.path.exists(animal[-1]):
                continue
            img = cv2.imread(animal[-1])
            animalName = animal[-2].replace(' ', '')
            img = cv2.resize(img, (600, 600))
            cv2.imwrite("{}/resizedImages/{}.jpg".format(ROOT, animalName), img)
            if len(numList) == 1:
                if numList[0] == 'Unknown':
                    altImage = 'Unknown'
                    numList[0] = 0
                    continue
                elif numList[0] == 'Extinct':
                    numList[0] = 0
                    altImage = 'Extinct'

                img = cv2.imread(str('{}/' + altImage + '.jpg').format(ROOT))
                img = cv2.resize(img, (800, 800))
                cv2.imwrite("{}/outputImages/{}.jpg".format(ROOT, animalName), img)
            else:
                sum = 0
                for num in numList:
                    sum += num
                if sum != 0:
                    avg = float(sum / float(len(numList)))
                    width = math.sqrt(avg)  # width and height are the same
                    height = int(math.ceil(width))
                    width = int(math.floor(width))
                    img = cv2.resize(img, (width, height))
                    img = cv2.resize(img, (800, 800), interpolation=cv2.INTER_NEAREST)
                    cv2.imwrite("{}/outputImages/{}.jpg".format(ROOT, animalName), img)

        tmp = []
        tmp.append(numList[0])
        for row in animal:
            tmp.append(row)
        tmp.append("{}/resizedImages/{}.jpg".format(ROOT, animalName))
        tmp.append("{}/outputImages/{}.jpg".format(ROOT, animalName))
        final_csv.append(tmp)

with open("{}/list.csv".format(ROOT), "w")as f:
    for row in final_csv:
        f.write(str(row) + "\n")

# image, pixel image, numbers to json them web[age
