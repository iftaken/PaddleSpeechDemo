import cairosvg
import os
 
 
# svg_path = '/Users/huangyiming02/Project/github/PaddleSpeechDemo/PaddleSpeechWebClient/src/assets/image/ic_大-上传文件.svg'
# png_path = 'ic_大-上传文件.png'
# cairosvg.svg2png(url=svg_path, write_to=png_path)

input_dir = "/Users/huangyiming02/Project/github/PaddleSpeechDemo/PaddleSpeechWebClient/src/assets/image"
output_dir = input_dir

for file in os.listdir(input_dir):
    if file.endswith(".svg"):
        print(file)
        infile = os.path.join(input_dir, file)
        outfile = os.path.join(output_dir, file.replace("svg", "png"))
        # print(outfile)
        cairosvg.svg2png(url=infile, write_to=outfile)


