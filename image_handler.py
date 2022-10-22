from PIL import Image

def update_locs(locs, batch):
    for row in batch:
        id,x,y, sos = row["ID"], row["x"], row["y"], row["SOS"]
        locs[id] = (x,y, sos)
    return locs

def convert_location(x, y, ego_x, ego_y):
    dis_x = ego_x - x
    dis_y = ego_y - y
    dis_x *= 100000
    dis_y *= 100000
    return int(dis_x) + 475, int(dis_y) + 475

def update_image(locs, ego_id):
    # locs is of form {id:(x,y)}
    background = Image.open("background.png")
    for id in locs:
        ego_x, ego_y,_ = locs[ego_id]
        x, y, sos = locs[id]
        if sos:
            car = Image.open(f"sos.png").convert("RGBA")
        elif id == ego_id:
            car = Image.open(f"self.png").convert("RGBA")
        else:
            car = Image.open(f"other.png").convert("RGBA")
        # resize image from before for performance
        car = car.resize((100, 100))
        x,y = convert_location(x,y, ego_x, ego_y)
        background.paste(car, (x,y), mask = car)
    return background