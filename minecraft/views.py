import json
import re
import subprocess
from os import listdir
from os.path import isfile, join

from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import UploadAddonForm

def execute_command(command):
    process = subprocess.Popen(command, shell=True,
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return stdout.decode('ascii')

def list_behavior_packs():
    mypath = '/data/behavior_packs'
    onlydirs = [f for f in listdir(mypath) if not isfile(join(mypath, f)) and f != 'chemistry' and not f.startswith('vanilla') and not f.startswith('test') and not f.startswith('experimental')]
    return onlydirs

def list_resource_packs():
    mypath = '/data/resource_packs'
    onlydirs = [f for f in listdir(mypath) if not isfile(join(mypath, f)) and f != 'vanilla' and f != 'chemistry']
    return onlydirs

def get_manifest_resource_pack(name):
    contents = get_file_contents('/data/resource_packs/{}/manifest.json'.format(name))
    if not contents:
        return None
    return json.loads(contents)

def get_manifest_behavior_pack(name):
    contents = get_file_contents('/data/behavior_packs/{}/manifest.json'.format(name))
    if not contents:
        return None
    return json.loads(contents)

def get_resource_pack_name_by_uuid(uuid):
    resource_packs = list_resource_packs()
    for resource_pack in resource_packs:
        manifest = get_manifest_resource_pack(resource_pack)
        if manifest and manifest['header']['uuid'] == uuid:
            return resource_pack
    return None

def get_resource_pack_uuid_by_name(name):
    manifest = get_manifest_resource_pack(name)
    if manifest:
        return manifest['header']['uuid']
    return None

def get_behavior_pack_name_by_uuid(uuid):
    behavior_packs = list_behavior_packs()
    for behavior_pack in behavior_packs:
        manifest = get_manifest_behavior_pack(behavior_pack)
        if manifest and manifest['header']['uuid'] == uuid:
            return behavior_pack
    return None

def get_behavior_pack_uuid_by_name(name):
    manifest = get_manifest_behavior_pack(name)
    if manifest:
        return manifest['header']['uuid']
    return None

def get_enabled_resource_packs(world):
    content = get_file_contents('/data/worlds/{}/world_resource_packs.json'.format(world))
    if not content:
        return []
    content = json.loads(content)
    enabled = []

    resource_packs = list_resource_packs()
    
    for item in content:
        for resource_pack in resource_packs:
            manifest = get_manifest_resource_pack(resource_pack)
            if manifest and manifest['header']['uuid'] == item['pack_id']:
                enabled.append(item)
    return enabled

def get_enabled_behavior_packs(world):
    content = get_file_contents('/data/worlds/{}/world_behavior_packs.json'.format(world))
    if not content:
        return []
    content = json.loads(content)
    enabled = []
    
    behavior_packs = list_behavior_packs()

    for item in content:
        for behavior_pack in behavior_packs:
            manifest = get_manifest_behavior_pack(behavior_pack)
            if manifest and manifest['header']['uuid'] == item['pack_id']:
                enabled.append(behavior_pack)
    return enabled

def enable_behavior_pack(world, behavior_pack):
    file_name = '/data/worlds/{}/world_behavior_packs.json'.format(world)
    content = get_file_contents(file_name)
    if not content:
        data = []
    else:
        data = json.loads(content)

    manifest = get_manifest_behavior_pack(behavior_pack)
    uuid = manifest['header']['uuid']

    for item in data:
        if item['pack_id'] == uuid:
            return

    data.append(
        {
            'pack_id': uuid,
            'version': manifest['header']['version']
        }
    )

    file_put_contents(file_name, json.dumps(data))
    restart_minecraft_server()

def request_enable_behavior_pack(request):
    enable_behavior_pack(get_current_map(), request.POST['behavior_pack'])
    return redirect('minecraft_list_maps')


def restart_minecraft_server():
    command = 'docker restart minecraft-bedrock-server'
    
    process = subprocess.Popen(command, shell=True,
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE)
    process.communicate()

def get_current_map():
    content = get_file_contents()
    map_name = re.search(r'level-name=(.*)', content).group(1)
    return map_name

def list_maps(request):
    mypath = '/data/worlds'
    onlydirs = [f for f in listdir(mypath) if not isfile(join(mypath, f))]
    map_name = ''
    content = get_file_contents()
    map_name = re.search(r'level-name=(.*)', content).group(1)

    upload_form = UploadAddonForm()

    command = 'docker exec minecraft-bedrock-server /usr/local/bin/mc-monitor status-bedrock --host 127.0.0.1 --port 19132'
    
    process = subprocess.Popen(command, shell=True,
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    status = stdout.decode('ascii')
    if not status:
        status = 'Offline ou reiniciando'

    return render(request, 'minecraft/list_maps.html', {
        'maps': onlydirs, 
        'current_map': map_name, 
        'status': status, 
        'upload_form': upload_form, 
        'behavior_packs': list_behavior_packs(), 
        'enabled_behavior_packs': get_enabled_behavior_packs(map_name)
    })

def get_file_contents(file_path='/data/server.properties'):
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            return content
    except FileNotFoundError:
        if file_path != '/data/server.properties':
            return ''
        raise FileNotFoundError

def file_put_contents(file_path, data):
    with open(file_path, 'w') as f:
        f.write(data)
        
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

def install_addon(request):
    if request.method == 'POST':
        form = UploadAddonForm(request.POST, request.FILES)
        if form.is_valid():
            f = request.FILES['file']
            file_name = f.name
            name = request.POST['name']
            addon_type = request.POST['addon_type']
            file_extension = file_name.split('.')[-1]
            file_only_name = file_name.split('.')[0]
            execute_command("mkdir -p /data/addons")

            path = '/data/addons/{}_{}.zip'.format(file_only_name, timezone.now().strftime('%Y-%m-%d-%H-%M-%S'))
            with open(path, 'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)

            if file_extension == 'mcaddon':
                execute_command("cd /data/addons/ && unzip {}".format(path))
                execute_command("cd /data/addons/ && unzip behavior.mcpack -d /data/behavior_packs/{}/ && unzip resource.mcpack -d /data/resource_packs/{}/ && rm -rf behavior.mcpack resource.mcpack".format(file_only_name, file_only_name))
            elif file_extension == 'mcpack' or file_extension == 'zip':
                if addon_type == 'behavior':
                    folder_name = 'behavior_packs'
                else:
                    folder_name = 'resource_packs'

                execute_command("cd /data/addons && unzip {} -d /data/{}/{}/".format(path, folder_name, name))

        return redirect('minecraft_list_maps')
        

