# run as `scrapy runspider mediareleases.py`

from io import BytesIO
from zipfile import ZipFile
import os
import re
import glob
import scrapy
import requests

os.makedirs("vault", exist_ok=True)


def parse_flickr_album(url):
	f = requests.get(url)
	local_images = []
	image_names = re.findall("live.staticflickr.com/\d+/(\d+?)_", f.text)
	image_names = list(set(image_names))
	for i in image_names:
		image_path = glob.glob('flickr/*' + i + "*")[0]
		print(image_path)
		local_images.append(image_path)
	return local_images


def parse_flickr(url):
	print ("Flickr link: " + url)
	if "sfupamr" in url:
		if "albums" in url or "sets" in url:
			images = parse_flickr_album(url)
			return images
		else:
			flickr_image = re.search('sfupamr/(\d+)', url).group(1)
			image_path = glob.glob('flickr/*' + flickr_image + "*")[0]
			print(image_path)
			return [image_path]
	else:
		return


class BlogSpider(scrapy.Spider):
	name = 'blogspider'
	start_urls = ['https://www.sfu.ca/university-communications/media-releases/media-release-archive.html']

	def parse_photos(self, response):
		for link in response.xpath('//a/@href'):
			url = link.get()
			if "at.sfu.ca" in url:
				r = requests.get(url, allow_redirects=False)
				if "vault" in r.text:
					vault_url = re.search('"https://vault.sfu.ca.*?"', r.text)
					if vault_url:
						vault_url = vault_url.group(0)
						print ("Vault link: " + url)
						zip_url = requests.get(vault_url.strip('"') + "/download")
						zipfile = ZipFile(BytesIO(zip_url.content))
						zip_names = zipfile.namelist()
						for name in zip_names:
							if "jpg" in name or "png" in name or "jpeg" in name:
								print(name)
								image_file = zipfile.open(name)
								vault_filename = os.path.join("vault", name.rsplit('/', 1)[-1])
								with open(vault_filename, 'wb') as vault_image:
									vault_image.write(image_file.read())
								with open("releases.txt", 'a') as releases:
									releases.write(vault_filename + " # " + response.meta['parent'] + "\n")
				elif "flickr" in r.text:
					flickr_url = re.search('"https://www.flickr.com.*?"', r.text)
					if flickr_url:
						local_list = parse_flickr(flickr_url.group(0))
						with open("releases.txt", 'a') as releases:
							for filename in local_list:
								releases.write(filename + " # " + response.meta['parent'] + "\n")
			elif "flickr.com" in url:
				local_list = parse_flickr(url)
				with open("releases.txt", 'a') as releases:
					for filename in local_list:
						releases.write(filename + " # " + response.meta['parent'] + "\n")

	def parse(self, response):
		for release in response.xpath('//li'):
			if release.xpath('.//span/@class').get() == 'news-date':
				with open("releases.txt", 'a') as releases:
					release_link = release.xpath('.//a/@href').get()
					releases.write(release_link + "\n")
					photo_response = response.follow(release_link, self.parse_photos)
					photo_response.meta['parent'] = release_link
					yield photo_response

		for nextpage in response.xpath('//div[@class="next"]/a[@href]'):
			yield response.follow(nextpage, self.parse)