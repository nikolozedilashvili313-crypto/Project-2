"""მოდელები: Entity, Task და TaskManager."""
from datetime import datetime

from exceptions import StorageError, TaskNotFoundError, ValidationError

PRIORITIES = ["low", "medium", "high"]
STATUSES = ["pending", "in-progress", "completed"]


class Entity:
    """ძირითადი კლასი ობიექტებისთვის, რომლებსაც უნიკალური ID აქვთ."""

    def __init__(self, entity_id):
        self._id = entity_id

    @property
    def id(self):
        return self._id


class Task(Entity):
    """ერთი დავალება. ველების ვალიდაცია ხდება property setter-ებში."""

    def __init__(self, task_id, title, description="", deadline="",
                 priority="medium", status="pending", project="general"):
        super().__init__(task_id)
        self.title = title
        self.description = description
        self.deadline = deadline
        self.priority = priority
        self.status = status
        self.project = project


    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        value = (value or "").strip()
        if not value:
            raise ValidationError("სათაური ცარიელი ვერ იქნება!")
        self._title = value

    @property
    def deadline(self):
        return self._deadline

    @deadline.setter
    def deadline(self, value):
        value = (value or "").strip()
        if value:
            try:
                datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                raise ValidationError("დედლაინი უნდა იყოს ფორმატით YYYY-MM-DD (მაგ. 2026-12-31)!")
        self._deadline = value

    @property
    def priority(self):
        return self._priority

    @priority.setter
    def priority(self, value):
        if value not in PRIORITIES:
            raise ValidationError(f"პრიორიტეტი უნდა იყოს: {', '.join(PRIORITIES)}")
        self._priority = value

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        if value not in STATUSES:
            raise ValidationError(f"სტატუსი უნდა იყოს: {', '.join(STATUSES)}")
        self._status = value

    @property
    def project(self):
        return self._project

    @project.setter
    def project(self, value):
        self._project = (value or "").strip().lower() or "general"


    def to_dict(self):
        """აბრუნებს დავალებას dict-ის სახით (JSON-ში შესანახად)."""
        return {"id": self.id, "title": self.title, "description": self.description,
                "deadline": self.deadline, "priority": self.priority,
                "status": self.status, "project": self.project}

    @staticmethod
    def from_dict(d):
        """ქმნის Task ობიექტს dict-იდან."""
        return Task(d["id"], d["title"], d.get("description", ""), d.get("deadline", ""),
                    d.get("priority", "medium"), d.get("status", "pending"),
                    d.get("project", "general"))

    def __str__(self):
        return (f"[{self.id}] {self.title} | {self.status} | {self.priority} "
                f"| დედლაინი: {self.deadline or '-'}")


class TaskManager:
    """მართავს დავალებების სიას და ინახავს მას storage-ის მეშვეობით."""

    def __init__(self, storage):
        self._storage = storage
        try:
            self._tasks = [Task.from_dict(d) for d in storage.load()]
        except (KeyError, TypeError):
            raise StorageError("ფაილის სტრუქტურა არასწორია.")
        self._next_id = max((t.id for t in self._tasks), default=0) + 1

    def save(self):
        """ინახავს ყველა დავალებას storage-ში."""
        self._storage.save([t.to_dict() for t in self._tasks])

    def get(self, task_id):
        """აბრუნებს დავალებას ID-ით ან ისვრის TaskNotFoundError-ს."""
        for t in self._tasks:
            if t.id == task_id:
                return t
        raise TaskNotFoundError(f"დავალება ID={task_id} ვერ მოიძებნა.")

    def add(self, title, description, deadline, priority, project):
        """ამატებს ახალ დავალებას (სტატუსი: pending)."""
        task = Task(self._next_id, title, description, deadline, priority, "pending", project)
        self._next_id += 1
        self._tasks.append(task)
        self.save()

    def edit(self, task_id, **changes):
        """ცვლის დავალების ველებს ატომურად.

        ვალიდაცია ხდება ახალ ობიექტზე; თუ რომელიმე ველი არასწორია,
        ორიგინალი დავალება არ იცვლება და ფაილშიც არაფერი იწერება.
        """
        task = self.get(task_id)
        updated = Task.from_dict({**task.to_dict(), **changes})
        self._tasks[self._tasks.index(task)] = updated
        self.save()

    def delete(self, task_id):
        """შლის დავალებას."""
        self._tasks.remove(self.get(task_id))
        self.save()

    def search(self, keyword):
        """ეძებს სათაურში, აღწერასა და პროექტის სახელში."""
        keyword = keyword.strip().lower()
        return [t for t in self._tasks
                if keyword in t.title.lower() or keyword in t.description.lower()
                or keyword in t.project]

    def grouped_by_project(self):
        """აბრუნებს dict-ს: პროექტის სახელი -> დავალებების სია."""
        groups = {}
        for t in self._tasks:
            groups.setdefault(t.project, []).append(t)
        return groups