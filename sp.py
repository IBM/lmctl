from lmctl.config import get_config


config = get_config()

sp_env = config.environments['mars'].site_planner


sp_client = sp_env.build_client()

rs = sp_client.pynb_api.dcim.devices.all()

print(type(rs))
print(rs.response)

print(next(rs.response))