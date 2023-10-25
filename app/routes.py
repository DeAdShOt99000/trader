from io import BytesIO
from datetime import datetime, timedelta

from flask import render_template, request, redirect, url_for, send_file, abort
from flask_login import current_user, login_required

from app import app, db, login_manager
from app.models import User, Item, Image, Chat
from app.forms import Sell

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

users_colors = {'a': '6290C8', 'b': '9ECE9A', 'c': '5D4E6D', 'd': '9B9ECE', 'e': 'FFAD05', 'f': 'D8315B', 'g': '60D394', 'h': 'C287E8', 'i': 'C0BDA5', 'j': 'CC978E', 'k': '03254E', 'l': '5E2BFF', 'm': 'A1683A', 'n': '499F68', 'o': '2E5EAA', 'p': 'E1CE7A', 'q': '48A9A6', 'r': '957FEF', 's': 'D78521', 't': '92140C', 'u': 'CDDFA0', 'v': '73C2BE', 'w': 'F7CB15', 'x': '878E88', 'y': '14453D', 'z': '48BEFF'}

def clean_dt(date_time: datetime):
    date = date_time.date()
    if date == datetime.today().date():
        clean_date = 'Today'
    elif date == (datetime.today().date() - timedelta(days=1)):
        clean_date = 'Yesterday'
    else:
        months = {1: 'Jan', 2: 'Feb', 3: 'Mar',
                  4: 'Apr', 5: 'May', 6: 'Jun',
                  7: 'Jul', 8: 'Aug', 9: 'Sep',
                  10: 'Oct', 11: 'Nov', 12: 'Dec'}
        clean_day = str(date.day)
        if clean_day[0] == '0':
            clean_day = clean_day[1]
        clean_date = f'{months[date.month]} {clean_day}, {date.year}'
    
    clean_minute = date_time.minute
    if len(str(clean_minute)) < 2:
        clean_minute = f'0{clean_minute}'
    
    if date_time.hour == 0:
        clean_time = f'12:{clean_minute} AM'
    elif date_time.hour < 13:
        clean_time = f'{date_time.hour}:{clean_minute} AM'
    else:
        clean_hour = date_time.hour - 12
        clean_time = f'{clean_hour}:{clean_minute} PM'
    return (clean_date, clean_time)

#--------------#

@app.get("/image/<int:img_id>")
def serve_image(img_id):
    image = Image.query.get(img_id)
    if image:
        return send_file(BytesIO(image.image), mimetype='image/jpeg')

@app.get("/")
def index():
    items = Item.query.all()
    return render_template("index.html", items=items)

@app.route("/sell", methods=("GET", "POST"))
@login_required
def sell():
    form = Sell()
    
    if form.validate_on_submit():
        item = Item(
            title=form.title.data,
            description=form.description.data,
            location=form.location.data,
            price=form.price.data,
            owner=current_user.id,
            created_at=datetime.now()
        )
        
        db.session.add(item)
        db.session.commit()
        
        image = Image(
            item_id=item.id
        )
        
        image_data = form.image.data.read()
        
        if len(image_data):
            image.image = image_data
        
        db.session.add(image)
        db.session.commit()
        return redirect(url_for("index"))
        
    return render_template("sell.html", form=form)

@app.get("/<int:item_id>/")
def single_item(item_id):
    items = []
    item = None
    
    for entry in Item.query.all():
        if entry.id == item_id:
            item = entry
            seller = User.query.get(item.owner)
        else:
            items.append(entry)
    
    if not item:
        abort(404)
    return render_template("single-item.html", items=items, item=item, seller=seller)

@app.get("/chats")
def chats():
    return render_template("chats.html")

@app.get("/chats/chats-json")
def chats_json():
    # all_friends = current_user.contacts.all()
    # chat_set = current_user.received_by_set.all()
    # af_dict_lst = []
    # if all_friends:
    #     for friend in all_friends:
    #         try:
    #             last_msg_details = chat_set.filter(sent_by=friend).order_by('-sent_at')[0]
    #             last_msg = (last_msg_details.text, timezone.localtime(last_msg_details.sent_at), last_msg_details.id)
    #         except:
    #             last_msg = ('', datetime(1, 1, 1), -1)
            
    #         try:
    #             not_viewed = len(chat_set.filter(sent_by=friend, viewed=False))
    #         except IndexError:
    #             not_viewed = None
            
    #         friend_dict = vars(friend)
    #         clean_friend_dict = {
    #             'id': friend_dict['id'],
    #             'username': friend_dict['username'],
    #             'first_name': friend_dict['first_name'].title(),
    #             'last_name': friend_dict['last_name'].title(),
    #             'email': friend_dict['email'],
    #             'not_viewed': not_viewed, # The number of unviewed messages
    #             'last_msg': last_msg, # Last message's text, time and id
    #             'user_color': users_colors[friend.first_name[0:1].lower()]
    #         }
    #         af_dict_lst.append(clean_friend_dict)

    #     sorted_dict_lst = sorted(af_dict_lst, key=lambda x: x['last_msg'][1].date(), reverse=True)
        
    #     if sorted_dict_lst[0]['last_msg'][2] != int(request.GET.get('last-msg-id')):
    #         return JsonResponse(sorted_dict_lst, safe=False)
    #     return JsonResponse([{'last_msg': 'same'}], safe=False)
    # return JsonResponse([], safe=False)
    
    all_friends = current_user.contacts.all()
    chat_set = current_user.received_chat
    print(all_friends)
    
    print([c.sent_by for c in chat_set])
    
    friends_dict_lst = []
    for friend in all_friends:
        friend_chat = list(filter(lambda f: f.sent_by == friend.id, chat_set))
        try:
            last_msg_details = friend_chat[-1]
            last_msg = (last_msg_details.text, last_msg_details.sent_at, last_msg_details.id)
        except:
            last_msg = ('', datetime(1, 1, 1), -1)
            
        try:
            not_viewed = len(list(filter(lambda f: f.viewed == False, friend_chat)))
        except IndexError:
            not_viewed = None
            
        clean_friend_dict = {
            'id': friend.id,
            'username': friend.username,
            'firstname': friend.firstname.title(),
            'lastname': friend.lastname.title(),
            'email': friend.email,
            'not_viewed': not_viewed, # The number of unviewed messages
            'last_msg': last_msg, # Last message's text, time and id
            'user_color': users_colors[friend.firstname[0:1].lower()]
        }
        
        friends_dict_lst.append(clean_friend_dict)
    sorted_lst = sorted(friends_dict_lst, key=lambda f: f['last_msg'][1].date(), reverse=True)
    
    if sorted_lst[0]['last_msg'][2] != int(request.args.get('last-msg-id')):
        return sorted_lst
    return {'last_msg': 'same'}
    
    # print(all_friends[0].id)
    # print(chat_set[0].sent_by)
    
@app.route("/chat/<int:user_id>", methods=('GET', 'POST'))
def single_chat(user_id):
    # contact = current_user.contacts.filter_by(id=user_id).first()
    contact = User.query.get_or_404(user_id)
    if not contact:
        abort(404)
    item_id = request.args.get('item-id')
        
    if request.method == "GET":
        return render_template('single-chat.html', contact=contact, item_id=item_id)
    
    elif request.method == 'POST':
        text_message = request.json['text-message']
        chat = Chat(
            text=text_message,
            sent_by=current_user.id,
            received_by=contact.id,
            sent_at=datetime.now(),
            item_id=request.json.get('item-id')
        )
        
        if contact not in current_user.contacts.all():
            current_user.contacts.append(contact)
            contact.contacts.append(current_user)
        
        db.session.add(chat)
        db.session.add(contact)
        db.session.add(current_user)
        db.session.commit()
        return {'message': 'Data received successfully'}

@app.get("/chat/<int:user_id>/chat-json")
def chat_json(user_id):
        try:
            friend = current_user.contacts.filter_by(id=user_id)[0]
        except:
            abort(404)
            
        item_id = request.args.get('item-id')
        
        chat_history = list(filter(lambda c: c.sent_by == current_user.id and c.received_by == friend.id or c.sent_by == friend.id and c.received_by == current_user.id, Chat.query.all()))
        
        if item_id:
            chat_history = list(filter(lambda x: str(x.item_id) == item_id, chat_history))
        
        ch_dict_lst = []
        if chat_history:
            for chat in chat_history:
                date_time = clean_dt(chat.sent_at)
                dict_entry = vars(chat)
                del dict_entry['_sa_instance_state']
                dict_entry.update({
                    'date': date_time[0],
                    'time': date_time[1]
                })
                ch_dict_lst.append(dict_entry)
            
            if ch_dict_lst[-1]['id'] != int(request.args.get('last-msg-id')):
                return ch_dict_lst
            return [{'id': 'same'}]
        return {}

@app.post("/chat/tag-as-viewed")
def tag_as_viewed():
    ids_lst = request.json['ids']
    for id in ids_lst:
        chat = Chat.query.get(id)
        chat.viewed = True
        db.session.add(chat)
        db.session.commit()
    return {'message': 'success!'}