from PIL import Image, ImageDraw, ImageFont
import math
import global_vars

def update_locs(locs, batch):
    for row in batch:
        id,x,y,t1_x,t1_y,t2_x,t2_y,msg = row["ID"], row["x"], row["y"], row["t1_x"], row["t1_y"], row["t2_x"], row["t2_y"], row["msg"]
        if not id:
            if id not in locs and len(locs) < 6:
                locs[id] = []
            t = (x,y)
            locs[id].append(t)
        else:
            locs[id] = (x,y,t1_x,t1_y,t2_x,t2_y,msg)
    return locs

def convert_location(x, y, ego_x, ego_y):
    dis_x = ego_x - x
    dis_y = ego_y - y
    dis_x *= 400000
    dis_y *= 400000
    return int(dis_x) + 475, int(dis_y) + 475

def update_image(locs, ego_id):
    # locs is of form {id:(x,y)}

    id_to_col = [0, "blue", "red", "green", "yellow"]

    background = Image.open("background.png")
    background = background.convert('RGB')


    if 0 in locs:
        for x, y in locs[0]:
            ego_x, ego_y,_,_,_,_,_ = locs[ego_id]
            x, y = convert_location(x, y, ego_x, ego_y)
            tree = Image.open(f"tree.png").convert("RGBA")
            tree = tree.resize((100, 100))
        background.paste(tree, (x, y), mask=tree)
    for id in locs:
        if id and id!=ego_id:
            ego_x, ego_y,_,_,_,_,_ = locs[ego_id]
            x, y, t1_x, t1_y, t2_x, t2_y, msg = locs[id]
            x,y = convert_location(x,y, ego_x, ego_y)
            
            if(x > 450 and x < 500 and y>450 and y<500):
                global_vars.collided=True
            
            destx,desty = convert_location(t1_x,t1_y, ego_x, ego_y)
            dest2x,dest2y = convert_location(t2_x,t2_y, ego_x, ego_y)
            if destx-x:
                theta = ((desty-y)/(destx-x))
            else:
                theta = 0
            angle = -math.degrees(math.atan(theta))
            if id == ego_id:
                car = Image.open(f"self.png").convert("RGBA")
            else:
                car = Image.open(f"other.png").convert("RGBA")
            # resize image from before for performance
            car = car.resize((100, 100))
            car = car.rotate(angle-90, Image.NEAREST, expand = 1)
            draw = ImageDraw.Draw(background)
            draw.line((x+50, y+50, destx+50, desty+50), fill=id_to_col[id], width=10)
            draw.line((destx+50, desty+50,dest2x+50, dest2y+50), fill=id_to_col[id], width=10)
            myFont = ImageFont.truetype('FreeMono.ttf', 65)
            draw.text((x, y-60), msg, font=myFont, fill=(255, 0, 0))
            background.paste(car, (x,y), mask = car)
    id = ego_id
    ego_x, ego_y,_,_,_,_,_ = locs[ego_id]
    x, y, t1_x, t1_y, t2_x, t2_y, msg = locs[id]
    x,y = convert_location(x,y, ego_x, ego_y)
    
    if(x > 450 and x < 500 and y>450 and y<500):
        global_vars.collided=True
    
    destx,desty = convert_location(t1_x,t1_y, ego_x, ego_y)
    dest2x,dest2y = convert_location(t2_x,t2_y, ego_x, ego_y)
    if destx-x:
        theta = ((desty-y)/(destx-x))
    else:
        theta = 0
    angle = -math.degrees(math.atan(theta))
    if id == ego_id:
        car = Image.open(f"self.png").convert("RGBA")
    else:
        car = Image.open(f"other.png").convert("RGBA")
    # resize image from before for performance
    car = car.resize((100, 100))
    car = car.rotate(angle-90, Image.NEAREST, expand = 1)
    draw = ImageDraw.Draw(background)
    draw.line((x+50, y+50, destx+50, desty+50), fill=id_to_col[id], width=10)
    draw.line((destx+50, desty+50,dest2x+50, dest2y+50), fill=id_to_col[id], width=10)
    myFont = ImageFont.truetype('FreeMono.ttf', 65)
    draw.text((x, y-60), msg, font=myFont, fill=(255, 0, 0))
    background.paste(car, (x,y), mask = car)
    return background