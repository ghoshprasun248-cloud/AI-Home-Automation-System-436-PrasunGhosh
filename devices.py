class Device:
    def __init__(self, id, name, state=False):
        self.id=id
        self.name=name
        self.state=state
    def to_dict(self):
        return {'id':self.id,'name':self.name,'state':self.state}

class DeviceManager:
    def __init__(self):
        self.devices={
            'light_living':Device('light_living','Living Room Light'),
            'plug_coffee':Device('plug_coffee','Coffee Maker Plug'),
            'thermostat':Device('thermostat','Thermostat')
        }
    def list_devices(self):
        return {k:v.to_dict() for k,v in self.devices.items()}
    def toggle_device(self, did):
        d=self.devices[did]
        d.state = not d.state
        return d.state
