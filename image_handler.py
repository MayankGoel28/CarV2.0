from PIL import Image, ImageDraw
import math

def update_locs(locs, batch):
    for row in batch:
        id,x,y,t1_x,t1_y,t2_x,t2_y = row["ID"], row["x"], row["y"], row["t1_x"], row["t1_y"], row["t2_x"], row["t2_y"]
        locs[id] = (x,y,t1_x,t1_y,t2_x,t2_y)
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

    for id in locs:
        ego_x, ego_y,_,_,_,_ = locs[ego_id]
        x, y, t1_x, t1_y, t2_x, t2_y = locs[id]
        x,y = convert_location(x,y, ego_x, ego_y)
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
        background.paste(car, (x,y), mask = car)
    return background