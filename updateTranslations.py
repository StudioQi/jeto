#-=- encoding: utf-8 -=-
import os
pybabel = 'pybabel'

os.system('pybabel extract -F babel.cfg -k lazy_gettext -o messages.pot\
          vagrantControl')
os.system('pybabel update -i messages.pot -d vagrantControl/translations')
os.unlink('messages.pot')
os.system('pybabel compile -d vagrantControl/translations')
