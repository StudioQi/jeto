#-=- encoding: utf-8 -=-
from jeto import db
from jeto.models.team import Team
# from jeto.models.vagrant import VagrantInstance

db.create_all()
#mock = VagrantInstance(1, '/home/lefebvre/Workbench/vagrant/', 'beikou', 'validation')
#db.session.add(mock)
db.session.commit()
