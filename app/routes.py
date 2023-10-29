from io import BytesIO
from datetime import datetime, timedelta
from cryptography.fernet import Fernet

from flask import render_template, request, redirect, url_for, send_file, abort, flash
from flask_login import current_user, login_required
from sqlalchemy import or_, and_

from app import app, db, login_manager
from app.models import User, Item, Image, Chat
from app.forms import Sell
from app.my_functions import formatted_dt


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

cipher = Fernet(b'Of_Jto2R-cJgpmgPE12NYPprUKpujfpZdsjkzWmIPZc=')

@app.get("/image/<int:img_id>")
def serve_image(img_id):
    image = Image.query.get(img_id)
    if image:
        return send_file(BytesIO(image.image), mimetype='image/jpeg')

@app.get("/")
def index():
    items = sorted(Item.query.all(), key=lambda x: x.created_at, reverse=True)
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
        flash("Item was added successfully!", 'success')
        return redirect(url_for("my_items"))
        
    return render_template("sell.html", form=form)

@app.get("/<int:item_id>/")
@login_required
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
    
    if current_user.is_authenticated:
        is_favourite = item in current_user.favourites
    else:
        is_favourite = False
    return render_template("single-item.html", items=items, item=item, seller=seller, is_favourite=is_favourite)

@app.get("/chats")
@login_required
def chats():
    return render_template("chats.html")

@app.get("/chats/chats-json")
def chats_json():
    my_contacts = set(current_user.contacts.all() + current_user.contacted_by.all())
    chat_set = current_user.received_chat
    
    if my_contacts:
        contacts_dict_lst = []
        for contact in my_contacts:
            contact_chat = list(filter(lambda c: c.sent_by == contact.id, chat_set))

            general_last_chat = Chat.query.filter(or_(and_(Chat.sent_by == current_user.id, Chat.received_by == contact.id), and_(Chat.sent_by == contact.id, Chat.received_by == current_user.id))).order_by(Chat.sent_at.desc()).all()[0]
            general_item = {'item_id': general_last_chat.item_id, 'item_title': Item.query.get(general_last_chat.item_id).title} if general_last_chat.item_id else None
            general_last_msg = (cipher.decrypt(general_last_chat.text).decode(), general_last_chat.sent_at, general_last_chat.id)
                
            not_viewed = len(list(filter(lambda c: c.viewed == False, contact_chat)))
            
            clean_contact_dict = {
                'id': contact.id,
                'username': contact.username,
                'firstname': contact.firstname.title(),
                'lastname': contact.lastname.title(),
                'email': contact.email,
                'not_viewed': not_viewed, # The number of unviewed messages
                'last_msg': general_last_msg, # Last message's text, time and id
                'item': general_item,
                'user_color': contact.profile_color
            }
            
            contacts_dict_lst.append(clean_contact_dict)
        sorted_lst = sorted(contacts_dict_lst, key=lambda c: c['last_msg'][1], reverse=True)
        
        if sorted_lst[0]['last_msg'][2] != int(request.args.get('last-msg-id')):
            return sorted_lst
        return {'last_msg': 'same'}
    return {}
    
@app.route("/chat/<int:user_id>", methods=('GET', 'POST'))
@login_required
def single_chat(user_id):
    contact = User.query.get_or_404(user_id)
    if not contact:
        abort(404)
    item_id = request.args.get('item-id')
        
    if request.method == "GET":
        next = request.args.get('next')
        return render_template('single-chat.html', contact=contact, item_id=item_id, next=next)
    
    elif request.method == 'POST':
        text_message = request.json['text-message']
        chat = Chat(
            text=cipher.encrypt(text_message.encode()),
            sent_by=current_user.id,
            received_by=contact.id,
            sent_at=datetime.now(),
            item_id=request.json.get('item-id')
        )
        
        if contact not in current_user.contacts.all() and current_user not in contact.contacts.all():
            current_user.contacts.append(contact)
        
        db.session.add(chat)
        db.session.commit()
        return {'message': 'Data received successfully'}

@app.get("/chat/<int:user_id>/chat-json")
def chat_json(user_id):
        try:
            contact = User.query.get(user_id)
        except:
            abort(404)
                    
        chat_history = list(filter(lambda c: c.sent_by == current_user.id and c.received_by == contact.id or c.sent_by == contact.id and c.received_by == current_user.id, Chat.query.all()))
                
        ch_dict_lst = []
        if chat_history:
            for chat in chat_history:
                date_time = formatted_dt(chat.sent_at)
                dict_entry = vars(chat)
                del dict_entry['_sa_instance_state']
                
                dict_entry.update({
                    'text': cipher.decrypt(dict_entry['text']).decode(),
                    'date': date_time[0],
                    'time': date_time[1],
                    'item_title': Item.query.get_or_404(dict_entry['item_id']).title if dict_entry['item_id'] else None,
                })
                ch_dict_lst.append(dict_entry)
            
            if ch_dict_lst[-1]['id'] != int(request.args.get('last-msg-id')):
                print(ch_dict_lst[-1]['id'], int(request.args.get('last-msg-id')))
                return ch_dict_lst
            return [{'id': 'same'}]
        return {}

@app.post("/chat/tag-as-viewed")
def tag_as_viewed():
    ids_lst = request.json['ids']
    for id in ids_lst:
        chat = Chat.query.get(id)
        chat.viewed = True
        db.session.commit()
    return {'message': 'success!'}

@app.get("/my-items")
@login_required
def my_items():
    items = Item.query.filter_by(owner=current_user.id).all()
    return render_template('my-items.html', items=items)

@app.get("/favourites")
@login_required
def favourites():
    fav_items = current_user.favourites
    return render_template('favourites.html', fav_items=fav_items)

@app.get("/favourite-json/<int:item_id>")
def favourite_json(item_id):    
    user_favourites = current_user.favourites
    item = Item.query.get_or_404(item_id)
    
    if item in user_favourites:
        user_favourites.remove(item)
        new_status = False
    else:
        user_favourites.append(item)
        new_status = True
        
    db.session.commit()
    
    return {'message': 'success', 'favourite': new_status}

@app.route("/my-items/edit/<int:item_id>", methods=('GET', 'POST'))
@login_required
def edit_item(item_id):
    item = Item.query.filter_by(id=item_id, owner=current_user.id).first_or_404()
    form = Sell(obj=item)
    
    if form.validate_on_submit():
        form.populate_obj(item)
        db.session.commit()
        
        next = request.args.get('next')
        
        flash("Item was successfully edited!", 'success')
        return redirect(next if next else url_for('my_items'))
    return render_template('edit-item.html', form=form)

@app.get("/my-items/delete/<int:item_id>")
@login_required
def delete_item(item_id):
    item = Item.query.filter_by(id=item_id, owner=current_user.id).first_or_404()
    
    for image in item.images:
        db.session.delete(Image.query.get(image.id))

    db.session.delete(item)
    db.session.commit()
    
    next = request.args.get('next')
        
    flash("Item was successfully deleted!", 'success')
    return redirect(next if next else url_for('my_items'))