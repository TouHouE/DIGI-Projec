def line_leave_park_message(owner: str, from_date, leave_date, cost: int, isStranger=False) -> str:
    def time_format(time) -> str:
        return f'{time.year}/{time.month}/{time.day} {time.hour}:{time.minute}:{time.second}'
    title = 'Hey! Stranger.' if isStranger else f'Hello {owner}!'
    duration = (leave_date - from_date).total_seconds()

    return f'\n{title}\nYour parking time is from \n{time_format(from_date)} ~ {time_format(leave_date)}\nDuration: {duration} seconds\nYou cost is: {cost}'