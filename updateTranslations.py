# -=- encoding: utf-8 -=-
import os
pybabel = 'pybabel'

os.system('pybabel extract -F babel.cfg -k lazy_gettext -o messages.pot jeto')
os.system('pybabel update -i messages.pot -d jeto/translations')
os.unlink('messages.pot')
os.system('pybabel compile -d jeto/translations')
