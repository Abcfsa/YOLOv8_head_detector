from ultralytics import YOLO
import glob,os
import pandas as pd
import argparse
def get_parser():
  num=len(glob.glob("./output_*.csv"))
  parser = argparse.ArgumentParser(description='setting parameters of the model.')
  parser.add_argument('--model',type=str,default='medium.pt',
                      help='path to the model parameters to be used by YOLO')
  parser.add_argument('--source',type=str,required=True,
                      help='path to the set of pics to detect heads from,must be a folder for now')
  parser.add_argument('--output',type=str,default="./output_%d.csv"%num,
                      help='path to the output_file.')
  parser.add_argument('--mode',type=str,default="detect",
                      help='mode of the model:detect or track.')
  return parser
  
if __name__ == "__main__":
  parser = get_parser()
  args = parser.parse_args()
  model=YOLO(args.model)
  #pics=os.listdir(args.source)
  if args.mode=='detect':
    df=pd.DataFrame(data=None,columns=['name','xmin','ymin','xmax','ymax'])
    results=model(args.source,stream=True)
    for result in results:
      box=result.boxes.cpu().numpy()
      for i in range(box.shape[0]):
        data=[result.path.split("/")[-1]]+list(box.xyxyn[i])
        df.loc[df.shape[0]]=data
    df.to_csv(args.output,index=False)
  elif args.mode=='track':
    df=pd.DataFrame(data=None,columns=['name','id','xmin','ymin','xmax','ymax'])
    results=model.track(args.source,stream=True,persist=True)
    for result in results:
      box=result.boxes.cpu().numpy()
      for i in range(box.shape[0]):
        if box.is_track is True:
          data=[result.path.split("/")[-1]]+[int(box.id[i])]+list(box.xyxyn[i])
          df.loc[df.shape[0]]=data
    df.to_csv(args.output,index=False)
  else:
    print("Please enter a proper mode.")
  