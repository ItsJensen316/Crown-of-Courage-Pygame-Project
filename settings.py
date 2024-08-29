import pygame,sys
from helper import *
import json

# Read data from JSON file

# Create the screen
def setting():
    def readFile(fname):
        with open(fname, "r") as json_file:
             fileInfo= json.load(json_file)
        return fileInfo     
    def writeFile(sourceFile,originalFile):
        with open(originalFile, "w") as json_file:
                    json.dump(sourceFile, json_file, indent=2)     
    # Initial settings
    setting=True
    sound_intensity = readFile("setting.json") # Value between 0 and 1
    print(sound_intensity)
    edit_img = set_image("./home_img/edit.png", (30,30))
    back_key_img=set_image("./home_img/back.png",(40,40))
    back_key_img_pos=(30,40)
    up=loadimages("home_img/up.png",(40,40))
    down=pygame.transform.flip(up, False, True)
    up_pos=(770,35)
    down_pos=(770,565)
    displace=0

    while setting:
        screen.fill((255,255,255))  # Clear the screen

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                if Rect(back_key_img,back_key_img_pos).collidepoint(mouse_pos):
                    # Handle game start button click
                    setting=False
                elif Rect(up,up_pos).collidepoint(mouse_pos) and displace+30<=0:
                    displace+=30 
                elif Rect(down,down_pos).collidepoint(mouse_pos):
                    displace-=30

        second_container_pos=(50,100)            
        mouse_pos = pygame.mouse.get_pos()
        control_keys=readFile("control_key.json") #reading the file data
     
        # screen.blit(blur_image(setting_bg,5),(0,0))
        H = pygame.font.Font(None, 30)
        head=pygame.font.Font(None,50)
        p=pygame.font.Font(None,20)
        p2=pygame.font.Font(None,24)
        # setting screen bg 
        screen.fill((79, 40, 0))
        draw_rect((0, 0, 0, 0.4),(50,100+displace,SCREEN_WIDTH-100,SCREEN_HEIGHT+50))
        draw_rect("YELLOW",(second_container_pos[0]+10,second_container_pos[1]+15+displace,5,10))
        draw_text("Sound",H,(230,230,230),second_container_pos[0]+50,second_container_pos[1]+20+displace)
        draw_rect((20,20,20),(second_container_pos[0]+15,second_container_pos[1]+40+displace,SCREEN_WIDTH-120,40))
        draw_text("Intensity" ,p2,(100,100,100),second_container_pos[0]+70,second_container_pos[1]+60+displace)
        # sound intensity area
        sound_line_start = (SCREEN_WIDTH//2+20, 160+displace)
        sound_line_end = (SCREEN_WIDTH-110, 160+displace)
        sound_value=sound_intensity["volume"]
        Vol_line=pygame.draw.line(screen, (0,0,0), sound_line_start, sound_line_end, 20)
        draw_text(f"{sound_value}" ,p2,(100,100,100),sound_line_start[0]-40,sound_line_start[1])
        pygame.draw.line(screen, (255, 255, 255), sound_line_start, sound_line_end, 2)
       

        # sound intesity section
        sound_circle_x = int(sound_line_start[0] + (sound_line_end[0] - sound_line_start[0]) * sound_value/100)
        sound_circle = pygame.draw.circle(screen, (0, 0, 0), (sound_circle_x, sound_line_start[1]), 8)
        if Vol_line.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
            sound_circle_x = mouse_pos[0]
            if sound_circle_x < sound_line_start[0]:
                sound_circle_x = sound_line_start[0]
            if sound_circle_x > sound_line_end[0]:
                sound_circle_x = sound_line_end[0]
            sound_intensity["volume"] = int((sound_circle_x - sound_line_start[0]) / (sound_line_end[0] - sound_line_start[0])*100)
        draw_rect("YELLOW",(sound_line_start[0],sound_line_start[1]-2,sound_circle_x-sound_line_start[0],5))
        sound_circle = pygame.draw.circle(screen, (255, 255, 255), (sound_circle_x, sound_line_start[1]), 8)
        writeFile(sound_intensity,"setting.json")

        # key section 
        draw_rect("YELLOW",(second_container_pos[0]+10,second_container_pos[1]+100+displace,5,10))
        draw_text("Controls",H,(230,230,230),second_container_pos[0]+60,second_container_pos[1]+90+15+displace)
        draw_text("Action",p,(200,200,200),second_container_pos[0]+60,second_container_pos[1]+120+15+displace)
        draw_text("Keys",p,(200,200,200),second_container_pos[0]+60+500,second_container_pos[1]+120+15+displace)
        # screen.blit(key_label, key_rect)

      

        for index, (action, key) in enumerate(control_keys.items()):
            height=165
            gap=40
            draw_rect((20,20,20),(second_container_pos[0]+15 ,second_container_pos[1]+150+gap*index+displace,SCREEN_WIDTH-120,30))
            draw_text(f"{action}" ,p2,(100,100,100),second_container_pos[0]+70,second_container_pos[1]+height +gap*index+displace)
            draw_text(f"{key}" ,p2,(100,100,100),second_container_pos[0]+70+500,second_container_pos[1]+height +gap*index+displace)
            pygame.draw.rect(screen,"WHITE",(second_container_pos[0]+40+500,second_container_pos[1]+height-15 +gap*index+displace,80,25),1)
            edit_img_pos=(second_container_pos[0]+60+600,second_container_pos[1]+height +gap*index+displace)
            edit_rect=edit_img.get_rect(center=edit_img_pos)
            screen.blit(edit_img,edit_rect)
            
            if edit_rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
                # print("collide")
              # Reset key temporarily
                pygame.draw.rect(screen,(20,20,20),(second_container_pos[0]+40+500,second_container_pos[1]+height-15 +gap*index+displace,80,25))
                draw_text("press key" ,p,(100,100,100),second_container_pos[0]+70+500,second_container_pos[1]+170 +50*index+displace)
                waiting_for_key = True
                while waiting_for_key:
                    for event in pygame.event.get():
                       
                        if event.type == pygame.KEYDOWN:
                            key_name = pygame.key.name(event.key)
                            print("Key pressed:", key_name)
                            control_keys[action] = key_name
                            waiting_for_key = False
                        pygame.display.flip()        
                writeFile(control_keys,"control_key.json")


        draw_rect("YELLOW",(second_container_pos[0]+10,second_container_pos[1]+490+displace,5,10))
        draw_text("Performance",H,(230,230,230),second_container_pos[0]+80,second_container_pos[1]+495+displace)
        draw_rect((20,20,20),(second_container_pos[0]+15,second_container_pos[1]+490+25+displace,SCREEN_WIDTH-120,40))
        draw_rect((255,255,255),(second_container_pos[0]+15,second_container_pos[1]+490+25+displace,25,25)) #Checkbox1
        draw_text("Low Graphics" ,p2,(100,100,100),second_container_pos[0]+80+10,second_container_pos[1]+495+40+displace)
        draw_rect((20,20,20),(second_container_pos[0]+15,second_container_pos[1]+490+75+displace,SCREEN_WIDTH-120,40))
        draw_text("Show FPS" ,p2,(100,100,100),second_container_pos[0]+80-5,second_container_pos[1]+495+90+displace)

        
        draw_rect((20,20,20),(0,0,800,80))
        draw_text(f"Settings",head,"white",SCREEN_WIDTH//2,50)
        # print(key_settings)
          # hover for return button
        hover([(up,up_pos)])
        hover([(down,down_pos)])
        hover([(back_key_img,back_key_img_pos)])

        pygame.display.flip()
