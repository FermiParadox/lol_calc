import user_instance_settings
from functional_testing.default_config import all_data_deepcopy


user_instance = user_instance_settings.UserSession()
combat_instance = user_instance.instance_after_combat(all_data_deepcopy())

output = {'history': combat_instance.combat_history,
          'results': combat_instance.combat_results}

print(str(output))
