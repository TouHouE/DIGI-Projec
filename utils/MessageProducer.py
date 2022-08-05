def line_leave_park_message(owner: str, from_date, leave_date, cost: int) -> str:
    def time_format(time) -> str:
        return f'{time.year}/{time.month}/{time.day} {time.hour}:{time.minute}'
    return f'\nHello {owner}!\nYour parking time is from \n{time_format(from_date)} ~ {time_format(leave_date)}\nYou cost is: {cost}'