from boto import ec2
from amazonControl import settings


class Amazon():
    def __init__(self):
        self.conn = ec2.connect_to_region(
            region_name=settings.region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key
        )

    def get_all_instances(self):
        instances = self._get_all_instances()
        instancesObjects = []
        for instance in instances:
            if instance.state != 'terminated':
                name = instance.__dict__['tags'].get('Name', None)
                project = instance.__dict__['tags'].get('Project', None)
                instancesObjects.append(
                    Instance(
                        instance.id,
                        name,
                        project,
                        instance.state,
                        instance.instance_type,
                        instance.ip_address,
                        instance.public_dns_name
                    )
                )
        return instancesObjects

    def _get_all_instances(self):
        instances = []
        reservations = self.conn.get_all_instances()
        for reservation in reservations:
            for instance in reservation.instances:
                instances.append(instance)

        return instances


class Instance():
    def __init__(
            self,
            id,
            name,
            project=None,
            state=None,
            instance_type=None,
            ip_address=None,
            public_dns_name=None,
            placement=None):

        self.id = id
        self.name = str(name)
        self.project = str(project)
        self.state = str(state)
        self.instance_type = str(instance_type)
        self.ip_address = str(ip_address)
        self.public_dns_name = str(public_dns_name)
        self.placement = str(placement)

    def __unicode__(self):
        return self.name
