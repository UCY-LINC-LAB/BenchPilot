from BenchPilotSDK.services.service import Service


class Mongodb(Service):
    """
    This class represents the mongodb docker service
    You can always change / add its supporting options
    """

    def __init__(self, options):
        Service.__init__(self)
        self.hostname = "mongodb"
        self.assign_image(image_name="benchpilot/benchpilot", image_tag=self.hostname, same_tag_for_all_arch=True)
        self.needs_placement = True
        self.service_started_log = "Starting"
        self.service_finished_log = "Finished"
        extra_parameters = options.extra_parameters if not options.extra_parameters is None else []
        for i in range(0, len(extra_parameters)):
            for opt_key in extra_parameters[i]:
                opt_value = extra_parameters[i][opt_key]
                if opt_key is str: 
                    opt_key = opt_key.upper()
                self.add_environment(env_name=opt_key, env_value=str(opt_value))


