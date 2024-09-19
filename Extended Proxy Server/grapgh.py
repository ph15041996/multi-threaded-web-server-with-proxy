# Get the no of user make request today ans show in graph
# Get the no of user make request in each  week
# Get the no of user make request in each month 
import json,os
from datetime import datetime, timedelta,date
import matplotlib.pyplot as plt
today = date.today()
today_day = today.day
one_week = timedelta(days=7)
one_month = timedelta(days=30)
json_file_path = "data.json"
isFilePresent = os.path.exists(json_file_path)
total_no_of_request = 0
request_made_today = 0
request_made_this_week= 0
request_made_this_month= 0
request_by_day = {
    'Sunday': 0,
    'Monday': 0,
    'Tuesday':0,
    'Wednesday':0,
    'Thursday':0,
    'Friday':0,
    'Saturday':0
}
month_names = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December"
}
request_by_month = {
    'January': 0,
    'February': 0,
    'March': 0,
    'April': 0,
    'May': 0,
    'June': 0,
    'July': 0,
    'August': 0,
    'September': 0,
    'October': 0,
    'November': 0,
    'December': 0
}

if(isFilePresent):
    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)
        for key,values in data.items():
            # print(key,values)
            for req in values:
                total_no_of_request+=1
                print(req["date_time"])
                get_date = req["date_time"].split(" ")[0]
                get_day_arr = get_date.split("-")
                get_day_no = get_day_arr[2]
                get_month_no = get_day_arr[1]
                date_time = datetime.strptime(req['date_time'], '%Y-%m-%d %H:%M:%S.%f')
                is_within_week = -(date_time.date()-today)<one_week
                is_within_month = -(date_time.date()-today)<one_month
                if(today_day == int(get_day_no)):
                    request_made_today += 1
                if(is_within_week):
                    request_made_this_week += 1
                    day_of_week = date_time.strftime('%A') 
                    request_by_day[day_of_week]+=1
                current_month_name = month_names[int(get_month_no)] 
                request_by_month[current_month_name]+=1
                if(is_within_month):
                    request_made_this_month+= 1

def plot_graph(x_axis,y_axis,name):
    print(y_axis)
    print(x_axis)
    plt.bar(x_axis,y_axis)
    plt.xticks( rotation=20, ha='right')
    plt.savefig(name,dpi=400)
    plt.close()
    # plt.show()
print(request_made_today)
print(request_made_this_week)
print(request_by_day)
print(request_by_month)
print(total_no_of_request)

my_axis = list(request_by_month.values())
mx_axis = list(request_by_month.keys())
plot_graph(mx_axis,my_axis,"request_by_month.png")



dy_axis = list(request_by_day.values())
dx_axis = list(request_by_day.keys())
plot_graph(dx_axis,dy_axis,"request_by_day.png")



tx_axis = ["Today"]
ty_axis = [request_made_today]
plot_graph(tx_axis,ty_axis,"request_made_today.png")
# x = np.array(["A", "B", "C", "D"])
# y = np.array([3, 8, 1, 10])
