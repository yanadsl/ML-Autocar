import RpiEnv
env = RpiEnv.Env()
while True:
    try:
        print(env.get_respond())
    except KeyboardInterrupt:
        env.end()