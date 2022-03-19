import re
import subprocess
from os import listdir
from os.path import isfile, join

from django.shortcuts import redirect, render

def restart_minecraft_server():
    command = 'docker restart minecraft-bedrock-server'
    
    process = subprocess.Popen(command, shell=True,
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE)
    process.communicate()

def list_maps(request):
    mypath = '/data/worlds'
    onlydirs = [f for f in listdir(mypath) if not isfile(join(mypath, f))]
    map_name = ''
    content = get_file_contents()
    map_name = re.search(r'level-name=(.*)', content).group(1)

    command = 'docker exec minecraft-bedrock-server /usr/local/bin/mc-monitor status-bedrock --host 127.0.0.1 --port 19132'
    
    process = subprocess.Popen(command, shell=True,
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    status = stdout.decode('ascii')
    if not status:
        status = 'Offline ou reiniciando'

    return render(request, 'minecraft/list_maps.html', {'maps': onlydirs, 'current_map': map_name, 'status': status})

def get_file_contents():
    with open('/data/server.properties', 'r') as f:
        content = f.read()
        return content
        
def change_map(request):
    if request.POST['map'] != '':
        content = get_file_contents()
        content = re.sub(r'level-name=.*', 'level-name=' + request.POST['map'], content)
        with open('/data/server.properties', 'w') as f:
            f.write(content)
        restart_minecraft_server()
    return redirect('minecraft_list_maps')
        

def create_map(request):
    if request.POST['map'] != '':
        content = get_file_contents()
        content = re.sub(r'level-name=.*', 'level-name=' + request.POST['map'], content)
        content = re.sub(r'level-seed=.*', 'level-seed=' + request.POST['seed'], content)
        with open('/data/server.properties', 'w') as f:
            f.write(content)
        restart_minecraft_server()
    return redirect('minecraft_list_maps')