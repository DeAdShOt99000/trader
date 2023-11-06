from io import BytesIO
from datetime import datetime
from cryptography.fernet import Fernet

from flask import render_template, request, redirect, url_for, send_file, abort, flash
from flask_login import current_user, login_required
from sqlalchemy import or_, and_

from app import app, db, login_manager
from app.models import User, Item, Image, Chat
from app.forms import SellEdit
from app.cust_formatting import DateTimeFormat


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Fernet object from cryptography module for encrypting and decrypting chat messages
cipher = Fernet(b'Of_Jto2R-cJgpmgPE12NYPprUKpujfpZdsjkzWmIPZc=')

# Route for retrieving item image
@app.get("/image/<int:img_id>")
def serve_image(img_id):
    image = Image.query.get(img_id)
    if image:
        return send_file(BytesIO(image.image), mimetype='image/jpeg')

# Index page that shows all items - Login not required
@app.get("/")
def index():
    items = Item.query.filter_by(is_sold=False).order_by(Item.created_at.desc()).all()
    return render_template("index.html", items=items)

@app.route("/sell", methods=("GET", "POST"))
@login_required
def sell():
    '''
    Route for selling new items - Login required
    
    It accepts GET and POST requests,
        GET: It takes you to a form that was constructed with flask_wtf forms for adding new item
        POST: takes the form that was submitted, validates all fields,
            - If the form was valid: Creates new item with the image that was provided in the form if the image exists, if the image
                                     was not provided, it uses a default image, and saves the item and the image in the database,
            redirects the user to 'My items' page with a success flash message.
            
            - If the form contains invalid data: Redirects the user to the same page with flash messages that shows the invalid fields.
    '''
    form = SellEdit()
    
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
        return redirect(url_for("active_items"))
        
    return render_template("sell.html", form=form)

@app.get("/<int:item_id>/")
def single_item(item_id):
    '''
    Route for viewing an item - Login not required
    
    it takes the item id as a parameter and shows the details of the item on the top part of the page,
    and it shows other items in the bottom part of the page. if the item does not exist, it shows
    a formatted 404 page.
    
    - It shows 2 buttons below item image:
        - If you are the seller of the item:
                - An 'Edit' button that routes the user to a form page for editing the item.
                - A 'Delete' button for deleting the item.
        - If you are not the seller of the item:
            - A 'Chat' button for chatting with the seller.
            - A 'Favourite' button for saving the item in 'My favourites' page.

        * If the user was not logged in and he clicked on a button, he will be redirected to login page with 'next' parameter in
        the url for getting back to the same page after logging in.
    '''
    items = []
    item = None
    
    for entry in Item.query.all():
        if entry.id == item_id:
            item = entry
            seller = User.query.get(item.owner)
        elif entry.is_sold == False:
            items.append(entry)
    
    if not item:
        abort(404)
    
    if current_user.is_authenticated:
        is_favourite = item in current_user.favourites
    else:
        is_favourite = False
    return render_template("single-item.html", items=items, item=item, seller=seller, is_favourite=is_favourite)

@app.get("/all-contacts")
@login_required
def all_contacts():
    '''
    Route that shows all contacts - Login required
    '''
    return render_template("all-contacts.html")

@app.get("/all-contacts/all-contacts-json")
@login_required
def all_contacts_json():
    '''
    A route that returns all contacts in JSON format - Login required
    
    The JSON object includes:
        - Contact details (ID, firstname, lastname, email, profile color)
        - Number of unviewed messages
        - Last message details (text, time sent, ID)
        - Related item details (ID, title) if the details were available
    
    The contacts are ordered by the last message's sending time from most recent message descendingly.
    
    It accepts 'last-msg-id' as a query parameter and checks if it matches JSON object's last
    message id, if it matches, it returns the JSON object {'last_msg': 'same'} instead of returning the
    whole list of contacts again.
    '''
    my_contacts = set(current_user.contacts.all() + current_user.contacted_by.all())
    chat_set = current_user.received_chat
    
    if my_contacts:
        contacts_dict_lst = []
        for contact in my_contacts:
            contact_chat = list(filter(lambda c: c.sent_by == contact.id, chat_set))

            general_last_chat = Chat.query.filter(or_(and_(Chat.sent_by == current_user.id, Chat.received_by == contact.id), and_(Chat.sent_by == contact.id, Chat.received_by == current_user.id))).order_by(Chat.sent_at.desc()).first()
            general_item = {'item_id': general_last_chat.item_id, 'item_title': Item.query.get(general_last_chat.item_id).title} if general_last_chat and general_last_chat.item_id else None
            general_last_msg = (cipher.decrypt(general_last_chat.text).decode(), general_last_chat.sent_at, general_last_chat.id) if general_last_chat else ('', datetime(1, 1, 1), -1)
                
            not_viewed = len(list(filter(lambda c: c.viewed == False, contact_chat)))
            
            clean_contact_dict = {
                'id': contact.id,
                'username': contact.username,
                'firstname': contact.firstname.title(),
                'lastname': contact.lastname.title(),
                'email': contact.email,
                'profile_color': contact.profile_color,
                'not_viewed': not_viewed, # The number of unviewed messages
                'last_msg': general_last_msg, # Last message's text, time and id
                'item': general_item,
            }
            
            contacts_dict_lst.append(clean_contact_dict)
        
        sorted_lst = sorted(contacts_dict_lst, key=lambda c: c['last_msg'][1], reverse=True)
        
        if sorted_lst[0]['last_msg'][2] != int(request.args.get('last-msg-id')):
            return sorted_lst
        return {'last_msg': 'same'}
    return {}

@app.get("/all-contacts/check-unread-json")
@login_required
def check_unread_json():
    '''
    Route for checking if there are any new unread messages - Login required.
    
    It takes the id of the person whom you are currently chatting with as an optional
    query parameter to ensure that the current chat is not marked as unraed as long as
    the chat page is open.
    
    it returns the total number of unread messages in JSON format.
    '''
    unread_chats = Chat.query.filter(Chat.received_by == current_user.id, Chat.viewed == False)
    
    exclude = request.args.get('exclude')
    
    if exclude:
        unread_chats = unread_chats.filter(Chat.sent_by != exclude)
        
    return {"unread_chats": len(unread_chats.all())}
    
@app.route("/chat/<int:user_id>", methods=('GET', 'POST'))
@login_required
def single_chat(user_id):
    '''
    Route that accepts GET and POST requests for viewing and sending chats with a specific user - Login required.
    
    It takes the id of the user to contact as a parameter.
        
    If the user to contact does not exist, it shows a formatted 404 page.
    
    If there was no previous chats between the two users, the two users will be
    added to user_contacts table in the database after the first chat message is
    sent.
    
    If this page was accessed from an item page, each sent chat will be saved with
    the related item id for context, and 'back' query parameter will be
    provided to get back to the item page instead of 'All contacts' page when you click on
    back button.
    
    The chats are saved in the database and each chat message text is encrypted
    before saving using Cryptography python module.
    '''
    contact = User.query.get_or_404(user_id)
    if not contact:
        abort(404)
    item_id = request.args.get('item-id')
        
    if request.method == "GET":
        back = request.args.get('back')
        return render_template('single-chat.html', contact=contact, item_id=item_id, back=back)
    
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
@login_required
def chat_json(user_id):
    '''
    Route for retrieving chat history of a user as a JSON object. - Login required
    
    if the user does not exist, it shows a formatted 404 page.
    
    The JSON object includes:
        - Chat details (ID, decrypted text message, sender ID, receiver ID, timestamp, item ID (if available))
        - Formatted date
        - Formatted time
        - Item title (if available)
        
    It accepts 'last-msg-id' as a query parameter and checks if it matches JSON object's last
    message id, if it matches, it returns the JSON object {'id': 'same'} instead of returning the
    whole chat history again.
    
    '''
    try:
        contact = User.query.get(user_id)
    except:
        abort(404)
                
    chat_history = list(filter(lambda c: c.sent_by == current_user.id and c.received_by == contact.id or c.sent_by == contact.id and c.received_by == current_user.id, Chat.query.all()))
            
    ch_dict_lst = []
    if chat_history:
        for chat in chat_history:
            date_time = DateTimeFormat(chat.sent_at)
            dict_entry = vars(chat)
            del dict_entry['_sa_instance_state']
            
            dict_entry.update({
                'text': cipher.decrypt(dict_entry['text']).decode(),
                'date': date_time.date_format(),
                'time': date_time.time_format(),
                'item_title': Item.query.get_or_404(dict_entry['item_id']).title if dict_entry['item_id'] else None,
            })
            ch_dict_lst.append(dict_entry)
        
        if ch_dict_lst[-1]['id'] != int(request.args.get('last-msg-id')):
            print(ch_dict_lst[-1]['id'], int(request.args.get('last-msg-id')))
            return ch_dict_lst
        return [{'id': 'same'}]
    return {}

@app.post("/chat/tag-as-viewed")
@login_required
def tag_as_viewed():
    '''
    Route for tagging a list of unviewed chats as viewed - Login required.
    
    It takes a list of IDs of unviewd chats as JSON object.
    
    returns a success message as JSON object.
    '''
    ids_lst = request.json['ids']
    for id in ids_lst:
        chat = Chat.query.get(id)
        chat.viewed = True
        db.session.commit()
    return {'message': 'success!'}

@app.get("/my-items/active")
@login_required
def active_items():
    '''
    Route that shows all of the current user's items - Login required
    '''
    items = Item.query.filter(Item.is_sold == False, Item.owner ==current_user.id).order_by(Item.created_at.desc()).all()
    return render_template('active-items.html', items=items)

@app.get("/my-items/sold")
@login_required
def sold_items():
    items = Item.query.filter(Item.is_sold == True, Item.owner == current_user.id).all()
    return render_template('sold-items.html', items=items)

@app.get("/my-items/status-toggle/<int:item_id>")
@login_required
def status_toggle(item_id):
    item = Item.query.filter(Item.id == item_id, Item.owner == current_user.id).first_or_404()
    
    item.is_sold = False if item.is_sold else True
    
    db.session.commit()
    
    if item.is_sold:
        flash('Item was marked as Sold successfully!', 'success')
    else:
        flash('Item was marked as Active successfully!', 'success')
    
    return redirect(request.referrer)

@app.get("/favourites")
@login_required
def favourites():
    '''
    Route that shows all items that the user tagged as favourite - Login required.
    '''
    fav_items = current_user.favourites
    return render_template('favourites.html', fav_items=fav_items)

@app.get("/favourite-json/<int:item_id>")
@login_required
def favourite_json(item_id):
    '''
    Route for tagging and untagging items as favourite - Login required.
    
    It takes the item to be tagged or untagged as a query parameter.
    
    It checks the status of the item and returns the new status as a JSON object.
        - If the item was already tagged, it untags it.
        - If it was untagged, it tags it.
    
    '''
    user_favourites = current_user.favourites
    item = Item.query.get_or_404(item_id)
    
    if item in user_favourites:
        user_favourites.remove(item)
        flash("Item was removed from favourites.", 'success')
        # new_status = False
    else:
        user_favourites.append(item)
        flash("Item was added to favourites!", 'success')
        # new_status = True
        
    db.session.commit()
        
    # return {'favourite': new_status}
    next = request.args.get('next')
    return redirect(next if next else url_for('favourites'))

@app.route("/my-items/edit/<int:item_id>", methods=('GET', 'POST'))
@login_required
def edit_item(item_id):
    '''
    Route that accepts GET and POST requests for editing current user's item - Login required.

    It takes the id of the item to be edited as a parameter,
    and if the item does not exist, it shows a formatted 404 page.
    
    When the editing form is submitted:
        - It checks if the updated item info is valid, if it was valid, it saves the updated item
        in the database and it redirects the user to 'My items' page if 'next' parameter was not provided
        in the url and it shows a success message, if it was not valid, it redirects the user to the same
        page with flash messages that shows the invalid fields.
    '''
    item = Item.query.filter_by(id=item_id, owner=current_user.id).first_or_404()
    image = Image.query.filter_by(item_id=item.id).first_or_404()
    form = SellEdit(obj=item)
    
    if form.validate_on_submit():
        form.populate_obj(item)
        image_data = form.image.data.read()
        if len(image_data):
            image.image = image_data
        db.session.commit()
        
        next = request.args.get('next')
        
        flash("Item was edited successfully!", 'success')
        return redirect(next if next else url_for('active_items'))
    return render_template('edit-item.html', form=form)

@app.get("/my-items/delete/<int:item_id>")
@login_required
def delete_item(item_id):
    '''
    Route for deleting current user item - Login required.
    
    It takes the id of the item to be deleted as a parameter,
    and if the item does not exist, it shows a formatted 404 page.
    
    It deletes the item and its corresponding image and redirects the
    user to 'My items' page if 'next' parameter was not provided in the
    url and it shows a success flash message.
    '''
    item = Item.query.filter_by(id=item_id, owner=current_user.id).first_or_404()
    
    for image in item.images:
        db.session.delete(Image.query.get(image.id))

    db.session.delete(item)
    db.session.commit()
    
    next = request.args.get('next')
        
    flash("Item was deleted successfully!", 'success')
    return redirect(next if next else url_for('active_items'))
        
