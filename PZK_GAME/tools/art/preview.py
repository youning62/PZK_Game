import sys
from PIL import Image
# usage: preview.py out.png img1 img2 ... (2 columns, 960 wide each)
out=sys.argv[1]; fs=sys.argv[2:]
ims=[]
for f in fs:
    im=Image.open(f)
    if im.mode=='RGBA':
        bg=Image.new('RGBA',im.size,(120,120,120,255)); bg.alpha_composite(im); im=bg
    im=im.convert('RGB'); im.thumbnail((960,960)); ims.append(im)
cols=2 if len(ims)>1 else 1
rows=(len(ims)+cols-1)//cols
cw=max(i.width for i in ims); ch=max(i.height for i in ims)
c=Image.new('RGB',(cw*cols,ch*rows),'black')
for k,i in enumerate(ims): c.paste(i,((k%cols)*cw,(k//cols)*ch))
c.save(out)
