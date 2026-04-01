from flask import Blueprint,render_template,request
import requests
import json
INSTANCE = "dev329383"
USERNAME = "admin"
PASSWORD = "B^xiDBx-p0Q3"
BASE_URL = f"https://{INSTANCE}.service-now.com/api/now/table/"
headers={
    "Accept":"application/json",
    "Context-Type":"application/json"
}
#通过incident number 寻找sys_id
def searchsysid(incident_number):
    table="incident"
    try:
        url = f"{BASE_URL}{table}?sysparm_query=number%3D{incident_number}&sysparm_fields=sys_id&sysparm_limit=1"
        res=requests.get(url,auth=(USERNAME,PASSWORD), headers=headers)
        res.raise_for_status()
        print(res.content)
        Result = json.loads(res.content)
        sysid=Result["result"][0]["sys_id"]
        print(f"SYS_ID is: {sysid}")
        return sysid
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e.response.text}")
    except Exception as e:
        print(f"Can not find ticket,please make sure the ticket number is right: {e}")
#创建incident 单子
cr =Blueprint("create",__name__)
@cr.route('/create',methods=["GET","POST"])
def create():
    if request.method == "GET":
        return render_template("create.html")
    
    short_description = request.form.get("description")
    urgency = request.form.get("urgency")
    table ="incident"
    url =f"{BASE_URL}{table}"
    playload = {
        "short_description":short_description,
        "urgency": urgency,
        "caller_id":"System Administrator"
        }
    try:
        res= requests.post(url,auth=(USERNAME,PASSWORD) ,headers=headers, data=json.dumps(playload))
        res.raise_for_status()
        new_record = res.json().get("result", {})
        ticketnumber = new_record.get('number')
        print(f"Incident Created successfully! Ticket Number: {ticketnumber}")
        return render_template("show.html",ticketno=ticketnumber)
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e.response.text}")
        return render_template("create.html",message=e.response.text)
    except Exception as e:
        print(f"Unknown Error: {e}")
        return render_template("create.html",message=e)
#查询单子    
@cr.route('/find',methods=["GET","POST"])
def find():
    if request.method=="GET":
        return render_template("find.html")
    findTickeNumber = request.form.get("ticketno")
    sys_id=searchsysid(findTickeNumber)
    table="incident"
    url =f"{BASE_URL}{table}{'/'}{sys_id}?sysparm_display_value=true&sysparm_fields=short_description%2Curgency%2Cstate%2Cwork_notes%2Ccomments"
    try:
        res=requests.get(url, auth=(USERNAME,PASSWORD), headers=headers )
        res.raise_for_status()
        Result = json.loads(res.content)
        print(Result)
        searchrecord =  res.json().get("result", {})
        searchshdescription =  searchrecord.get('short_description')
        searchurgency = searchrecord.get('urgency')
        searchstate = searchrecord.get('state')
        searchcomment = searchrecord.get('comments')
        searchworknotes = searchrecord.get('worknotes')
        return render_template("information.html",tkno=findTickeNumber,tkdescript=searchshdescription,tkurgency=searchurgency,tkstate=searchstate,tkcomment = searchcomment,tkworknotes =searchworknotes)
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e.response.text}")
        return render_template("information.html",message=e.response.text)
    except Exception as e:
        print(f"Unknown Error: {e}")
        return render_template("information.html",message=e)
#删除单子
@cr.route('/delete',methods=["GET","POST"])
def delete():
    if request.method=="GET":
        return render_template("delete.html")
    deleteticketnumber= request.form.get("ticketno")
    sys_id=searchsysid(deleteticketnumber)
    table="incident"
    url=f"{BASE_URL}{table}{'/'}{sys_id}"
    try:
        res=requests.delete(url, auth=(USERNAME,PASSWORD), headers=headers )
        if res.status_code == 204:
            print("Successfully Deleted")
            return render_template("successful.html",tkno=deleteticketnumber)
        else:
            return render_template("delete.html",message =f"Can't delete {deleteticketnumber},please check!" )
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e.response.text}")
        return render_template("delete.html",message = e.response.text)
    except Exception as e:
        print(f"Unknown Error: {e}")
        return render_template("delete.html",message = e)
#修改单子    
@cr.route('/modify',methods=["GET","POST"])
def modify():
    if request.method=="GET":
        return render_template("modify.html")
    else:
        buttonvalue= request.form.get("button-modify")
        modifynumber = request.form.get("ticket-number")
        sys_id=searchsysid(modifynumber)
        table="incident"
        searchurgency=""
        searchstate=""
        if buttonvalue == "findticket":
            url =f"{BASE_URL}{table}{'/'}{sys_id}?sysparm_display_value=true&sysparm_fields=short_description%2Curgency%2Cstate%2Cwork_notes%2Ccomments"
            try:
                res=requests.get(url, auth=(USERNAME,PASSWORD), headers=headers )
                res.raise_for_status()
                searchrecord =  res.json().get("result", {})
                searchshdescription =  searchrecord.get('short_description')
                searchurgency = searchrecord.get('urgency')
                searchstate = searchrecord.get('state')
                print(searchstate)
                print(searchurgency)
                print(searchshdescription)
                return render_template("modify.html",tkno=modifynumber,tkdescription=searchshdescription,
                               tkurgency = searchurgency,tkstate=searchstate)
            except requests.exceptions.HTTPError as e:
                print(f"HTTP error: {e.response.text}")
                return render_template("modify.html",message = e.response.text)
            except Exception as e:
                print(f"can't find the record please make sure it exits: {e}")
                return render_template("modify.html",message = "can't find the record please make sure it exits")
        elif buttonvalue == "update":
            modifyurl = f"{BASE_URL}{table}{'/'}{sys_id}?sysparm_display_value=True&sysparm_input_display_value=True"
            playload = {}
            notes = request.form.get("worknotes")
            newurgency = request.form.get("urgency")
            newstate = request.form.get("state")
            if notes is not None:
                playload.update({"work_notes":notes})
            if newurgency != searchurgency:
                playload.update({"urgency":newurgency})
            if newstate !=searchstate:
                playload.update({"state":newstate})
            try:
                res= requests.patch(modifyurl,auth=(USERNAME,PASSWORD) ,headers=headers,data=json.dumps(playload))
                if res.status_code == 200: 
                    print("Successfully Modified")
                    return render_template("modifysuccessful.html",tkno=modifynumber)
                else:
                    print('Status:', res.status_code, 'Headers:', res.headers, 'Error Response:',res.json())
                    return render_template("modify.html",message = "Failed to update")
            except requests.exceptions.HTTPError as e:
                        print(f"HTTP Error: {e.response.text}")
            except Exception as e:
                    print(f"Unknown Error: {e}")
                