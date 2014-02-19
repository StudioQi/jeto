#-=- encoding: utf-8 -=-
from vagrantControl import db
from vagrantControl.models import VagrantInstance

db.create_all()
#mock = VagrantInstance(1, '/home/lefebvre/Workbench/vagrant/', 'beikou', 'validation')
#db.session.add(mock)
db.session.commit()
