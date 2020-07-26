import json
import pandas as pd
import requests

def get_json(url):
	print(url)
	r = requests.get(url, verify=False)
	numtext = r.text
	return json.loads(numtext)

def get_oid_title(content_type, identity):
	if content_type == 'video':
		bv_url = f'http://api.bilibili.com/x/web-interface/view?bvid={identity}'
		bv_status = get_json(bv_url)
		oid = bv_status['data']['aid']
		title = bv_status['data']['title']
		ctype = 1
	elif content_type == 'dynamic':
		dynamic_url = f'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/get_dynamic_detail?dynamic_id={identity}'
		dynamic_status = get_json(dynamic_url)
		oid = dynamic_status['data']['card']['desc']['rid']
		title = identity
		ctype = 11
	return oid, title, ctype

def get_pages(oid, ctype):
	base_url = f'https://api.bilibili.com/x/v2/reply?type={ctype}&pn=1&oid={oid}&sort=2'
	base_json = get_json(base_url)
	return ((int(base_json['data']['page']['count'])//int(base_json['data']['page']['size'])) + 1)

def get_result(content_url):
	content_url = content_url.split('?')[0]
	content_type = 'video' if 'video' in content_url else 'dynamic'
	identity = content_url.split('/')[-1]

	oid, title, ctype = get_oid_title(content_type, identity)
	pages = get_pages(oid, ctype)

	res = []
	for i in range(1, pages+1):
		url = f'https://api.bilibili.com/x/v2/reply?type={ctype}&pn={i}&oid={oid}&sort=2'
		print(url)
		r = requests.get(url, verify=False)
		numtext = r.text
		data = json.loads(numtext)

		reply_list = data['data']['replies']

		for item in reply_list:
			res.append([item['content']['message'], item['like'], item['rcount'], \
						list(item['content']['emote'].keys()) if 'emote' in item['content'] else ''])

		if pages == 1:
			break

	df = pd.DataFrame(res, columns=['Content', 'Like', 'Reply', 'Emotion'])
	print(df)
	return df, title

if __name__ == '__main__':
	content_url = 'https://www.bilibili.com/video/BV1QK411n7oT'
	# content_url = 'https://t.bilibili.com/411576107406760613'
	df, title = get_result(content_url)
	df.to_csv(f'{title}.csv', encoding='utf-8-sig')