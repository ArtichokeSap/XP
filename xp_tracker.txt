import json
import datetime
import copy

class Task:
    def __init__(self, name, category, duration, stat, date=None):
        if isinstance(date, str):
            date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        self.name = name
        self.category = category
        self.duration = duration  # in minutes
        self.stat = stat
        self.date = date or datetime.date.today()

    def to_tuple(self):
        return (self.name, self.category, self.duration, self.stat, self.date.isoformat())

    @classmethod
    def from_tuple(cls, tpl):
        return cls(*tpl)

class User:
    def __init__(self):
        self.tasks = []
        self.xp = 0
        self.level = 1
        self.streaks = {}
        self.stats = {k: 0 for k in ('Body','Mind','Art','Tech','Home','Spirit')}
        # Undo/Redo history
        self._history = []
        self._hist_index = -1
        self._snapshot()

    def _snapshot(self):
        # prune forward history
        self._history = self._history[:self._hist_index+1]
        state = {
            'tasks': [t.to_tuple() for t in self.tasks]
        }
        self._history.append(state)
        self._hist_index += 1

    def undo(self):
        if self._hist_index > 0:
            self._hist_index -= 1
            self._restore(self._history[self._hist_index])

    def redo(self):
        if self._hist_index < len(self._history)-1:
            self._hist_index += 1
            self._restore(self._history[self._hist_index])

    def _restore(self, state):
        self.tasks = [Task.from_tuple(t) for t in state['tasks']]
        self._recalculate()

    def add_task(self, task):
        self.tasks.append(task)
        self._recalculate()
        self._snapshot()

    def update_task(self, idx, task):
        self.tasks[idx] = task
        self._recalculate()
        self._snapshot()

    def delete_task(self, idx):
        del self.tasks[idx]
        self._recalculate()
        self._snapshot()

    def _recalculate(self):
        # reset stats
        self.xp = 0
        self.streaks.clear()
        for k in self.stats: self.stats[k]=0
        # sort tasks
        for t in sorted(self.tasks, key=lambda t: t.date):
            bonus = 1
            if t.category in ('typing','piano'):
                prev = self.streaks.get(t.category)
                if prev and (t.date - prev[-1]).days == 1:
                    streak_len = len(prev) + 1
                    bonus = min(streak_len, 3)
                    prev.append(t.date)
                else:
                    self.streaks[t.category] = [t.date]
            # xp gain
            gain = t.duration * bonus
            self.xp += gain
            self.stats[t.stat] += gain
        self.level = self.xp // 600 + 1

    def save_to_json(self, filename):
        data = {
            'tasks': [t.to_tuple() for t in self.tasks],
        }
        with open(filename, 'w') as f:
            json.dump(data, f)

    def load_from_json(self, filename):
        with open(filename, 'r') as f:
            data = json.load(f)
        self.tasks = [Task.from_tuple(t) for t in data.get('tasks', [])]
        self._recalculate()
        self._snapshot()

if __name__ == '__main__':
    # simple CLI test
    u = User()
    u.add_task(Task('Test', 'reading', 30, 'Mind', '2025-05-18'))
    print('XP:', u.xp, 'Level:', u.level)
    u.undo()
    print('After undo - tasks:', len(u.tasks))
    u.redo()
    print('After redo - tasks:', len(u.tasks))
