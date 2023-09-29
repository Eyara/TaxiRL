import numpy as np


class ReplayManager:
    def __init__(self):
        self.filename = 'train_states.txt'

    def save_to_file(self, training_states):
        np.set_printoptions(threshold=np.inf, linewidth=np.inf)

        with open('./%s' % self.filename, 'w') as f:
            cur_episode = -1

            for i in training_states:
                if cur_episode < i[0]:
                    cur_episode += 1
                    f.write('Episode: %s \n' % cur_episode)

                f.write(np.array2string(np.array(i[1]), separator=', '))
                f.write('\n')
