import RpiEnv

env = RpiEnv.Env()

while True:
    try:
        receive_data = env.get_respond()
        env.test(receive_data)
    except KeyboardInterrupt:
        env.end()
