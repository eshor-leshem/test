#! /usr/bin/python3

import argparse
import utils
import sys
import time
import random

mac_addresses = {'elad': '84:77:77:77:77:77', 'efrat': '84:88:88:88:88:88', 'anna': '84:99:99:99:99:99' }


def arg_parser():
    parser = argparse.ArgumentParser(
        description='Etool Clips',
        usage=
        '''
        e.g. etool_clips.py --id aws_access_keyID --key secret_accessKEY --as_url https://52.30.231.86 --ap_url https://eu-innovi-staging.agentvi.com --name elad --builds build-dev-3695 build-rc-1.2.1-3664
        '''
    )
    parser.add_argument('--id', help="The aws access id", type=str, required=True)
    parser.add_argument('--key', help="The aws access key", type=str, required=True)
    parser.add_argument('--name', help="Your name to load customize env configuration (elad/efrat/anna) ",
                        choices=['elad', 'efrat', 'anna'], type=str, required=True)
    parser.add_argument('--builds', help="The desired build names (for e.g build-dev-3695 build-rc-1.2.1-3664)",
                        nargs='+', type=str, required=True)
    parser.add_argument('--amount', help="How many clips to create for each build", type=int, default=10)
    parser.add_argument('--as_url', help="AS URL", type=str, required=True)
    parser.add_argument('--ap_url', help="Admin Portal URL", type=str, required=True)
    parser.add_argument('-k', help="Do not delete previous machine clips", action='store_true', default=False)
    parser.add_argument('--region', help="The aws region (default: us-west-2)", type=str, default="us-west-2")
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit("\nPlease see Usage")
    return parser.parse_args()


def main():
    args = arg_parser()
    new_request = utils.EncoderClip(args.id, args.key, args.region, args.name, args.builds)
    if not args.k:
        exists_machine = new_request.current_running_instances('Etool_Encoder_{}'.format(args.name))
        if exists_machine:
            new_request.terminate_instances(exists_machine)
    new_instance_id = new_request.create_clip_encoder()
    new_request.is_instance_status_ok(new_instance_id)
    new_instance_ip = new_request.instance_id_to_ip(new_instance_id)
    # new_instance_ip = '52.43.10.30'

    retries = 6
    while retries != 0:
        try:
            start_clips = utils.Ssh(new_instance_ip, 'ubuntu')
        except Exception as err:
            print("SSH to Encoder machine ({}) failed:{}\nRetrying...".format(new_instance_ip, err))
            retries -= 1
            time.sleep(10)
        else:
            break
    else:
        raise Exception("Couldn't connect to clip machine({}) Exiting!".format(new_instance_ip))

    clips = [clip for clip in start_clips.execute_to_list('ls -l Clips/|grep avi|awk \'{print $9}\'')]
    index = 0
    for build in args.builds:
        for _ in range(args.amount):
            start_clips.execute(
                'sudo docker run -d --restart unless-stopped --name=TEST_{} -e MAC_ADDRESS={} '
                '-e AGENT_ID={} --log-opt max-size=1m --log-opt max-file=3 -e AS_URL={} '
                '-v ~/Clips:/Clips -e CLIP_URL=/Clips/{} -e PAIRING_KEY=c80423d3-1518-4e5c-a5d8-e4a5db978958 '
                'agentvi/vi-agent-appliance:{}'.format(
                    index, mac_addresses[args.name], index, args.as_url, random.choice(clips).strip(), build)
                )
            index += 1


if __name__ == '__main__':
    main()