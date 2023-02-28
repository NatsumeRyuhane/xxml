import miraicle
import logging

# Login
bot = miraicle.Mirai(qq = 1411434717, verify_key = 'mirai.auth(0)', port = 8088)
logging.debug("Bot instance created successfully")


def reply_plain_text(context: miraicle.Message, message: str, add_mention: bool = False, use_quote = True):
    message_out = []
    message_out.append(miraicle.Plain(message))
    
    quote_msg_id = None
    if use_quote:
        quote_msg_id = context.id
    
    if isinstance(context, miraicle.GroupMessage):
        if add_mention:
            message_out.insert(0, miraicle.At(qq = context.sender))

        bot.send_group_msg(group = context.group, 
                                 msg = message_out,
                                 quote = quote_msg_id)
        
    elif isinstance(context, miraicle.TempMessage):
        bot.send_temp_msg(group = context.group,
                                qq = context.sender,
                                msg = message_out)

    elif isinstance(context, miraicle.FriendMessage):
        bot.send_friend_msg(qq = context.sender,
                                  msg = message_out)

    else: raise TypeError("Unrecognized message context type!")

def reply_image(context: miraicle.Message, message: str, image_path: [], add_mention: bool = False, use_quote = True):
    message_out = []

    if not isinstance(image_path, list):
        image_path = [image_path]

    if image_path:
        for i in image_path:
            message_out.append(miraicle.Image(base64 = i))
    message_out.append(miraicle.Plain(message))
    
    quote_msg_id = None
    if use_quote:
        quote_msg_id = context.id
    
    if isinstance(context, miraicle.GroupMessage):
        if add_mention:
            message_out.insert(0, miraicle.At(qq = context.sender))

        bot.send_group_msg(group = context.group, 
                                 msg = message_out,
                                 quote = quote_msg_id)
        
    elif isinstance(context, miraicle.TempMessage):
        bot.send_temp_msg(group = context.group,
                                qq = context.sender,
                                msg = message_out)

    elif isinstance(context, miraicle.FriendMessage):
        bot.send_friend_msg(qq = context.sender,
                                  msg = message_out)

    else: raise TypeError("Unrecognized message context type!")