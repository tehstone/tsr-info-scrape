import re
import requests
from bs4 import BeautifulSoup
from pokedict import poke_dict

task_page = "https://thesilphroad.com/research-tasks/"
poke_regex = re.compile("\d+x\d+/(?P<dexid>\d+)\.[a-zA-Z]{3}")
page = requests.get(task_page)
soup = BeautifulSoup(page.content, 'html.parser')

task_groups = soup.findAll('div', attrs={'class': 'task-group'})
with open('new_quest_data.json','w') as file:
    file.write('[\n')
    firstgroup = True
    for group in task_groups:
        
        tasks = group.findAll('div', attrs={'class': 'task'})
        for task in tasks:
            if not firstgroup:
                file.write(',\n')
            else:
                firstgroup = False
            quest = task.find('p', attrs={'class': 'taskText'})
            file.write(f'\t{{\n\t\t"name": "{quest.text}",\n\t\t"reward_pool": {{\n')
            rewards = task.findAll('div', attrs={'class': 'task-reward'})
            reward_pool = {"encounters": [], "stardust": [], "items": {}}
            for reward in rewards:
                rewardtype = reward.attrs["class"][1]
                if rewardtype == "pokemon":
                    urlstr = reward.find('img')
                    m = poke_regex.search(urlstr.attrs['src'])
                    if m:
                        rewardvalue = m.group('dexid')
                        reward_pool["encounters"].append(poke_dict[int(rewardvalue)])
                    else:
                        continue
                elif rewardtype == "stardust":
                    reward_pool["stardust"].append(reward.text)
                else:
                    reward_pool["items"][rewardtype] = reward.text
            for key, value in reward_pool.items():
                file.write(f'\t\t\t"{key}": ')
                if key == "encounters":
                    if len(value) > 0:
                        file.write('["')
                        file.write('","'.join(value))
                        file.write('"],\n')
                    else:
                        file.write('[],\n')
                elif key == "stardust":
                    if len(value) > 0:
                        file.write(f'[{value[0]}],\n')
                    else:
                        file.write('[],\n')
                elif key == "items":
                    if len(value) > 0:
                        file.write('{\n')
                        first = True
                        for ikey, ival in value.items():
                            if not first:
                                file.write(',\n')
                            else:
                                first = False
                            file.write(f'\t\t\t\t"{ikey}": [{ival}]')
                        file.write('\n\t\t\t}\n')
                    else:
                        file.write('{}\n')
            file.write('\t\t}\n\t}')
            
    file.write('\n]')


