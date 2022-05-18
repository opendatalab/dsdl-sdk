#########################################################################
#    > File Name: convert2dsdl.py
#    > Author: Bin Wang
#    > Created Time: Tue 17 May 2022 07:33:40 AM UTC
#    > Desciption: 提取json文件中的标注信息，写入dsdl对应的data samples 
#########################################################################
#-*-coding:utf-8-*-
import json
import pdb


def write_sample(sample, file_point):
  """ 提取sample信息，并格式化写入yaml文件
  sample = {
      'media': {'path':xxx, 'source':xxx, 'type':'image', 'height':xxx, 'width: xxx'},
      'ground_truth': {list of {'bbox':[x1,y1,w,h], 'ann_id':xxx,..., 'categories:[{}]'}}
  }
  """
  image_path = sample['media']['path']
  file_point.writelines(f'\t\t- image: "{image_path}"\n')
  file_point.writelines(f'\t\t  objects:\n')
  gts = sample['ground_truth']
  for i in range(len(gts)):
    [x1, y1, w, h] = gts[i]['bbox']
    cls = gts[i]['categories'][0]['category_id']
    file_point.writelines(f'\t\t\t  - {{ bbox: [{x1}, {y1}, {w}, {h}], label: {cls}}}\n')


if __name__ == '__main__':

  src_file = './json/train.json'
  out_file = './demo2/data_samples.yaml'

  with open(src_file) as fp:
    train_data = json.load(fp)

  with open(out_file, 'w') as fp:
    fp.writelines('data:\n')
    fp.writelines('\tsample-type: ObjectDetectionSample[cdom=VOCClassDom]\n')
    fp.writelines('\tsamples:\n')
    
    samples = train_data['samples']
    for i in range(len(samples)):
      write_sample(samples[i], fp)

