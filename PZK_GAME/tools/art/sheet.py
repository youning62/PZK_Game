import sys,glob,os
from PIL import Image,ImageDraw
# sheet.py out.png crop_top_frac files...  -> shows upper part of sprites on checker bg
out=sys.argv[1]; frac=float(sys.argv[2]); fs=sys.argv[3:]
ims=[]
for f in fs:
    im=Image.open(f).convert('RGBA'); w,h=im.size
    im=im.crop((0,0,w,int(h*frac)))
    bg=Image.new('RGBA',im.size,(150,160,150,255)); bg.alpha_composite(im)
    bg=bg.convert('RGB'); bg.thumbnail((400,400)); ImageDraw.Draw(bg).text((4,4),os.path.basename(f)[:28],fill='black')
    ims.append(bg)
cols=5; rows=(len(ims)+cols-1)//cols
cw=max(i.width for i in ims); ch=max(i.height for i in ims)
c=Image.new('RGB',(cw*cols,ch*rows),'white')
for k,i in enumerate(ims): c.paste(i,((k%cols)*cw,(k//cols)*ch))
c.save(out)
