from argparse import ArgumentParser
import pdb


def main():
    parser = ArgumentParser()
    main_arg_group = parser.add_mutually_exclusive_group(required=True)
    main_arg_group.add_argument('--address', type=str)
    main_arg_group.add_argument('--zip', type=str)
    args = parser.parse_args()

    # pdb.set_trace()
    print('Running!')


if __name__ == '__main__':
    main()
