"""Task Manager: კონსოლური მენიუ და პროგრამის შესასვლელი წერტილი."""
from decorators import handle_errors, log_action
from exceptions import TaskError, ValidationError
from models import PRIORITIES, STATUSES, TaskManager
from storage import JsonStorage

MENU = """
========== TASK MANAGER ==========
1. დავალების დამატება
2. დავალებების ნახვა (პროექტების მიხედვით)
3. ძებნა
4. რედაქტირება
5. სტატუსის შეცვლა
6. წაშლა
0. გასვლა
=================================="""


def ask(prompt):
    """კითხულობს შეყვანას და აშორებს ზედმეტ ინტერვალებს."""
    return input(prompt).strip()


def pick(prompt, options, default=None):
    """მომხმარებელი ირჩევს ნომრით (1, 2, 3...). ცარიელი = default."""
    value = ask(prompt)
    if not value:
        return default
    if not value.isdigit() or not 1 <= int(value) <= len(options):
        raise ValidationError("აირჩიეთ სიაში მითითებული ნომერი.")
    return options[int(value) - 1]


def ask_id(prompt="დავალების ID: "):
    """კითხულობს დავალების ID-ს და ამოწმებს, რომ ის მთელი რიცხვია."""
    value = ask(prompt)
    if not value.isdigit():
        raise ValidationError("ID უნდა იყოს დადებითი მთელი რიცხვი.")
    return int(value)


def show(tasks):
    """ბეჭდავს დავალებების სიას."""
    if not tasks:
        print("დავალებები ვერ მოიძებნა.")
    for t in tasks:
        print("  ", t)


@handle_errors
@log_action("დავალება დაემატა!")
def add_task(tm):
    """ამატებს ახალ დავალებას."""
    title = ask("სათაური: ")
    description = ask("აღწერა: ")
    deadline = ask("დედლაინი (YYYY-MM-DD, არასავალდებულო): ")
    priority = pick("პრიორიტეტი (1-low, 2-medium, 3-high, ცარიელი = medium): ", PRIORITIES, default="medium")
    project = ask("პროექტი (ცარიელი = general): ")
    tm.add(title, description, deadline, priority, project)


@handle_errors
def list_tasks(tm):
    """აჩვენებს დავალებებს პროექტების მიხედვით."""
    groups = tm.grouped_by_project()
    if not groups:
        print("დავალებები ჯერ არ არის.")
    for project, tasks in sorted(groups.items()):
        print(f"\nპროექტი: {project}")
        show(tasks)


@handle_errors
def search_tasks(tm):
    """ეძებს დავალებებს საკვანძო სიტყვით."""
    show(tm.search(ask("საძიებო სიტყვა: ")))


@handle_errors
@log_action("დავალება განახლდა!")
def edit_task(tm):
    """არედაქტირებს დავალებას. ცარიელი ველი = უცვლელი, '-' = დედლაინის გასუფთავება."""
    task_id = ask_id()
    task = tm.get(task_id)
    print("დატოვეთ ცარიელი, თუ არ გინდათ შეცვლა (დედლაინის წასაშლელად შეიყვანეთ -).")
    fields = {
        "title": ask(f"სათაური [{task.title}]: "),
        "description": ask(f"აღწერა [{task.description}]: "),
        "deadline": ask(f"დედლაინი [{task.deadline}]: "),
        "priority": pick(f"პრიორიტეტი [{task.priority}] (1-low, 2-medium, 3-high): ", PRIORITIES),
        "project": ask(f"პროექტი [{task.project}]: "),
    }
    changes = {k: v for k, v in fields.items() if v}
    if changes.get("deadline") == "-":
        changes["deadline"] = ""
    tm.edit(task_id, **changes)


@handle_errors
@log_action("სტატუსი შეიცვალა!")
def change_status(tm):
    """ცვლის დავალების სტატუსს."""
    task_id = ask_id()
    status = pick("სტატუსი (1-pending, 2-in-progress, 3-completed): ", STATUSES)
    tm.edit(task_id, status=status)


@handle_errors
@log_action("დავალება წაიშალა!")
def delete_task(tm):
    """შლის დავალებას ID-ით."""
    tm.delete(ask_id())


def main():
    """პროგრამის მთავარი ციკლი: ჩატვირთვა, მენიუ, შენახვა გასვლისას."""
    try:
        tm = TaskManager(JsonStorage("tasks.json"))
    except TaskError as e:
        print(f"პროგრამა ვერ ჩაიტვირთა: {e}")
        return

    actions = {"1": add_task, "2": list_tasks, "3": search_tasks,
               "4": edit_task, "5": change_status, "6": delete_task}
    try:
        while True:
            print(MENU)
            choice = ask("აირჩიეთ: ")
            if choice == "0":
                break
            action = actions.get(choice)
            if action:
                action(tm)
            else:
                print("არასწორი არჩევანი.")
    except (KeyboardInterrupt, EOFError):
        print()
    try:
        tm.save()
    except TaskError as e:
        print(f"შეცდომა: {e}")
    print("ნახვამდის!")


if __name__ == "__main__":
    main()