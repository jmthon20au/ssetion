from telethon import TelegramClient, events, utils
from telethon.sessions import StringSession
from telethon.tl.functions.account import UpdateProfileRequest, GetAuthorizationsRequest, ResetAuthorizationRequest
from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest, CreateChannelRequest, EditAdminRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.functions.users import GetFullUserRequest 
from telethon.tl.types import Channel, Chat, UserFull, ChannelParticipantsAdmins, ChannelParticipantCreator, ChannelParticipantAdmin
from telethon.errors.rpcerrorlist import UsernameNotOccupiedError, UsernameInvalidError, FloodWaitError
import asyncio
import os
import re 

# --- اعداداتك الأساسية والمطلوبة ---
api_id = 21756632         # <<<< استبدل هذا بـ API ID الخاص بك (هو رقم)
api_hash = '57f991d0be16dc7c6f836dc342181541'   # <<<< استبدل هذا بـ API HASH الخاص بك (هو سلسلة نصية بين علامتي اقتباس)
bot_token = '7453332492:AAEmHz3Ol8AE78GZ0vrYxmxL_I7SzPEwohE'  # <<<< استخدم التوكن الصحيح الخاص ببوتك!
your_user_id = 6454550864 # <<<< استخدم الـ ID الصحيح الخاص بك!

# --- متغيرات البوت ---
user_string_session = None 
user_client = None
bot_client = TelegramClient('bot_session', api_id, api_hash)

# متغيّرات لحالة إنشاء البوت - هذه المتغيرات عامة ويتم تعديلها باستخدام 'global'
is_creating_bot = False
temp_bot_name = None
temp_bot_username = None
temp_event_to_reply = None 

async def start_user_client():
    global user_client
    if user_string_session and (not user_client or not user_client.is_connected()):
        print("جاري محاولة تسجيل الدخول إلى الحساب الشخصي باستخدام StringSession...")
        try:
            if user_client and user_client.is_connected():
                await user_client.disconnect()
                print("تم فصل العميل القديم للحساب الشخصي قبل إعادة الاتصال.")
            
            user_client = TelegramClient(StringSession(user_string_session), api_id, api_hash)
            await user_client.start()
            
            me = await user_client.get_me()
            print(f"✅ تم تسجيل الدخول بنجاح إلى الحساب الشخصي: {utils.get_display_name(me)}")
            await bot_client.send_message(your_user_id, 
                                          f"✅ تم تسجيل الدخول بنجاح إلى حسابك: **{utils.get_display_name(me)}**\n"
                                          "يمكنك الآن إرسال أوامر التحكم.\n"
                                          "اكتب /help  لعرض الأوامر.")
        except Exception as e:
            print(f"❌ حدث خطأ أثناء تسجيل الدخول إلى الحساب الشخصي: {e}")
            await bot_client.send_message(your_user_id, 
                                          f"❌ فشل تسجيل الدخول إلى حسابك الشخصي: `{e}`\n"
                                          "الرجاء التأكد من صحة StringSession وأنه لم تنته صلاحيته.")
            user_client = None
    elif user_client and user_client.is_connected():
        print("عميل الحساب الشخصي متصل بالفعل.")
    else:
        print("لم يتم تلقي StringSession بعد لبدء عميل الحساب الشخصي.")

@bot_client.on(events.NewMessage(incoming=True))
async def bot_handler(event):
    global is_creating_bot, temp_bot_name, temp_bot_username, temp_event_to_reply

    if event.sender_id != your_user_id:
        await event.reply("عزيزي المستخدم لتستخدم البوت لان ما يستجيبلك 😉🤖 فقط الادمن راسل @altaee_z لصناعة بوت مماثل 🌸 www.ali-Altaee.free.nf")
        return

    message_text = event.raw_text.strip()
    command = message_text.split(' ', 1)[0].lower()

    if is_creating_bot and event.sender_id == your_user_id:
        if temp_bot_name is None:
            temp_bot_name = message_text
            try:
                bot_father_entity = await user_client.get_entity('BotFather')
                await user_client.send_message(bot_father_entity, '/newbot') 
                await asyncio.sleep(1) 
                await user_client.send_message(bot_father_entity, temp_bot_name)
                await temp_event_to_reply.reply("✅ تم إرسال اسم البوت إلى BotFather. الآن **أرسل لي يوزرنيم البوت (يجب أن ينتهي بـ `bot`):**")
                print(f"[LOG] تم إرسال اسم البوت ({temp_bot_name}) إلى BotFather.")
            except Exception as e:
                await temp_event_to_reply.reply(f"❌ حدث خطأ أثناء إرسال اسم البوت: `{e}`. يرجى المحاولة مرة أخرى.")
                is_creating_bot = False
                temp_bot_name = None
                temp_bot_username = None
                temp_event_to_reply = None
            return 

        elif temp_bot_username is None:
            temp_bot_username = message_text
            try:
                bot_father_entity = await user_client.get_entity('BotFather')
                await user_client.send_message(bot_father_entity, temp_bot_username)
                await temp_event_to_reply.reply("✅ تم إرسال يوزرنيم البوت إلى BotFather. جاري انتظار رسالة التوكن...")
                print(f"[LOG] تم إرسال يوزرنيم البوت ({temp_bot_username}) إلى BotFather.")
                
                @user_client.on(events.NewMessage(chats='BotFather', incoming=True))
                async def bot_token_handler(event_from_botfather):
                    global is_creating_bot, temp_bot_name, temp_bot_username, temp_event_to_reply 

                    print(f"[DEBUG] Received message from BotFather in handler: {event_from_botfather.raw_text}") 
                    
                    if "Done! Congratulations on your new bot." in event_from_botfather.raw_text or \
                       "Sorry, the username is already taken" in event_from_botfather.raw_text or \
                       re.search(r'HTTP API:\s*`(\d+:[a-zA-Z0-9_-]+)`', event_from_botfather.raw_text):
                        
                        await temp_event_to_reply.reply(f"🎉 **لقد تلقيت ردًا من BotFather بخصوص البوت الجديد!**\n\n"
                                                      f"**هذه هي الرسالة الكاملة التي تلقيتها:**\n"
                                                      f"\n{event_from_botfather.raw_text}\n\n\n"
                                                      f"**يرجى البحث عن توكن البوت الخاص بك داخل هذه الرسالة.**")
                        
                        print(f"[LOG] تم إعادة توجيه رسالة BotFather الكاملة.")
                        user_client.remove_event_handler(bot_token_handler) 
                        is_creating_bot = False
                        temp_bot_name = None
                        temp_bot_username = None
                        temp_event_to_reply = None
                    elif "Invalid bot short name" in event_from_botfather.raw_text or "name is too short" in event_from_botfather.raw_text:
                         await temp_event_to_reply.reply("❌ عذراً، اسم البوت أو يوزرنيم البوت غير صالح. الرجاء المحاولة مرة أخرى باستخدام `/create_bot` واسم/يوزرنيم صالح.")
                         user_client.remove_event_handler(bot_token_handler)
                         is_creating_bot = False
                         temp_bot_name = None
                         temp_bot_username = None
                         temp_event_to_reply = None
                    else:
                        print(f"[DEBUG] رسالة BotFather لم يتم التعرف عليها، جاري الانتظار: {event_from_botfather.raw_text}")

            except Exception as e:
                await temp_event_to_reply.reply(f"❌ حدث خطأ أثناء إرسال يوزرنيم البوت: `{e}`. يرجى المحاولة مرة أخرى.")
                is_creating_bot = False
                temp_bot_name = None
                temp_bot_username = None
                temp_event_to_reply = None
            return 

    if command == '/start':
        await event.reply(
        "مرحباً بك! أنا بوت التحكم بحسابك الشخصي.\n"
        "للبدء، أرسل لي StringSession الخاص بحسابك.\n"
        "إذا كنت لا تعرف كيف تحصل عليه، راجع التعليمات في السكريبت.\n"
        "www.ali-Altaee.free.nf"
    )
        if user_client and user_client.is_connected():
            await event.reply("حسابك الشخصي متصل بالفعل. يمكنك الآن إرسال الأوامر.")
        else:
            await event.reply("حسابك الشخصي غير متصل بعد. الرجاء إرسال StringSession باستخدام الأمر /session")

    elif command == '/session':
        if len(message_text.split(' ', 1)) > 1:
            global user_string_session
            user_string_session = message_text.split(' ', 1)[1]
            await event.reply("✅ تم استلام StringSession. جاري محاولة تسجيل الدخول إلى حسابك الشخصي...")
            await start_user_client()
        else:
            await event.reply("دز السيشن  بأستخدام /session")
    
    elif command == '/help':
        help_message = """
**أوامر التحكم بالحساب (عبر البوت):**
  - /session <StringSession> : لإرسال StringSession الخاص بحسابك وتسجيل الدخول.
  -  /info : لعرض معلومات حسابك الشخصي **مع صورة الحساب**.
  -  /change_name <الاسم الجديد>: لتغيير اسم العرض الخاص بك.
  -  /change_bio <البايو الجديد>: لتغيير الوصف الشخصي (البايو).
  -  /change_pic <مسار_الصورة>: لتغيير صورة ملفك الشخصي.
  -  /change_username <اليوزرنيم_الجديد> : لتغيير اليوزرنيم الخاص بحسابك.
  -  /join <رابط_الدعوة_أو_يوزرنيم_القناة/الكروب>: للانضمام إلى قناة أو مجموعة.
  -  /leave <يوزرنيم_القناة/الكروب> : لمغادرة قناة أو مجموعة.
  -  /msg <يوزرنيم_الشخص> <الرسالة> : لإرسال رسالة لشخص معين عن طريق اليوزرنيم.
  - /create_bot: لبدء عملية إنشاء بوت جديد عبر BotFather (سيطلب منك الاسم واليوزرنيم).
  - /create_channel <اسم_القناة> [الوصف]: لإنشاء قناة جديدة.
  - /create_group <اسم_الكروب> : لإنشاء مجموعة جديدة (ستدخلها أنت فقط).
  - /list_joined_chats : لعرض جميع القنوات والمجموعات التي انضممت إليها.
  - /list_my_managed_chats : لعرض جميع القنوات والمجموعات التي تديرها أو تملكها.
  - /list_sessions : لعرض جميع جلسات تسجيل الدخول النشطة لحسابك.
  - /remove_session <الرقم_المراد_حذفه>`: لإزالة جلسة تسجيل دخول محددة.
  -  /ping : للتحقق من أن البوت والحساب يعملان.
  -  /help : لعرض هذه المساعدة.
  -  /stop : لإيقاف البوت والحساب بشكل آمن.
"""
        await event.reply(help_message)

    # أوامر التحكم بالحساب الشخصي (يجب أن يكون user_client متصلاً)
    elif user_client and user_client.is_connected():
        if command == '/info':
            user_id = 'غير متاح'
            first_name = 'غير متاح'
            last_name = ''
            username = 'غير متاح'
            bio_text = 'لا يوجد'
            two_factor_status = 'غير متاح' 
            profile_photo_sent = False

            try:
                me = await user_client.get_me()
                user_id = str(me.id)
                first_name = me.first_name or 'لا يوجد'
                last_name = me.last_name or ''
                username = me.username or 'لا يوجد'
                
                # إرسال صورة البروفايل أولاً
                if me.photo:
                    try:
                        photo_path = await user_client.download_profile_photo(me.id)
                        if photo_path:
                            await event.reply(file=photo_path, message="صورة ملفك الشخصي:")
                            os.remove(photo_path) # حذف الصورة بعد الإرسال
                            profile_photo_sent = True
                    except Exception as e:
                        print(f"[ERROR] خطأ أثناء إرسال صورة البروفايل: {e}")
                        await event.reply("⚠️ لا يمكن إرسال صورة ملفك الشخصي حالياً.")
                
                full_me = await user_client(GetFullUserRequest(me.id))
                
                if full_me:
                    bio_text = full_me.about or 'لا يوجد'
                    two_factor_status = 'مفعل' if full_me.has_password else 'غير مفعل'
            
            except Exception as e_main:
                print(f"[ERROR] خطأ عام في جلب معلومات الحساب: {e_main}")
            
            user_info_message = (
                f"**معلومات حسابك:**\n"
                f"  - **الاسم:** `{first_name} {last_name}`\n"
                f"  - **اليوزرنيم:** `@{username}`\n"
                f"  - **ID:** `{user_id}`\n"
                f"  - **البايو:** `{bio_text}`\n"
                f"  - **التحقق بخطوتين (2FA):** `{two_factor_status}`"
            )
            await event.reply(user_info_message)
            print(f"[LOG] تم عرض معلومات الحساب.")


        elif command == '/change_name':
            if len(message_text.split(' ', 1)) > 1:
                new_name = message_text.split(' ', 1)[1]
                try:
                    first_name_part = new_name.split(' ', 1)[0]
                    last_name_part = new_name.split(' ', 1)[1] if ' ' in new_name else ''
                    await user_client(UpdateProfileRequest(first_name=first_name_part, last_name=last_name_part))
                    await event.reply(f"✅ تم تغيير الاسم بنجاح إلى: **{new_name}**")
                    print(f"[LOG] تم تغيير الاسم إلى: {new_name}")
                except Exception as e:
                    await event.reply(f"❌ حدث خطأ أثناء تغيير الاسم: `{e}`")
                    print(f"[ERROR] خطأ في تغيير الاسم: {e}")
            else:
                await event.reply("الرجاء تحديد اسم جديد بعد الأمر، مثال: `/change_name اسمي الجديد`")

        elif command == '/change_bio':
            if len(message_text.split(' ', 1)) > 1:
                new_bio = message_text.split(' ', 1)[1]
                try:
                    await user_client(UpdateProfileRequest(about=new_bio))
                    await event.reply(f"✅ تم تغيير البايو بنجاح إلى: **{new_bio}**")
                    print(f"[LOG] تم تغيير البايو إلى: {new_bio}")
                except Exception as e:
                    await event.reply(f"❌ حدث خطأ أثناء تغيير البايو: `{e}`")
                    print(f"[ERROR] خطأ في تغيير البايو: {e}")
            else:
                await event.reply("الرجاء تحديد بايو جديد بعد الأمر، مثال: `/change_bio هذا هو البايو الخاص بي`")
        
        elif command == '/change_pic':
            if len(message_text.split(' ', 1)) > 1:
                photo_path = message_text.split(' ', 1)[1]
                if os.path.exists(photo_path):
                    try:
                        await user_client.upload_profile_photo(photo_path)
                        await event.reply(f"✅ تم تغيير صورة البروفايل بنجاح من المسار: `{photo_path}`")
                        print(f"[LOG] تم تغيير صورة البروفايل من: {photo_path}")
                    except Exception as e:
                        await event.reply(f"❌ حدث خطأ أثناء تغيير صورة البروفايل: `{e}`")
                        print(f"[ERROR] خطأ في تغيير الصورة: {e}")
                else:
                    await event.reply(f"❌ مسار الصورة غير صحيح أو الملف غير موجود: `{photo_path}`")
                    print(f"[ERROR] مسار صورة غير صالح: {photo_path}")
            else:
                await event.reply("الرجاء تحديد مسار الصورة بعد الأمر، مثال: `/change_pic /sdcard/Download/my_pic.jpg`")

        elif command == '/change_username':
            if len(message_text.split(' ', 1)) > 1:
                new_username = message_text.split(' ', 1)[1]
                try:
                    # هذه هي الطريقة الصحيحة لتغيير اليوزرنيم في Telethon
                    # Note: You must ensure the username is available and valid.
                    await user_client(UpdateProfileRequest(username=new_username))
                    await event.reply(f"✅ تم تغيير اليوزرنيم بنجاح إلى: **@{new_username}**")
                    print(f"[LOG] تم تغيير اليوزرنيم إلى: @{new_username}")
                except UsernameInvalidError:
                    await event.reply("❌ اليوزرنيم غير صالح (قد يحتوي على أحرف غير مسموح بها أو غير متوفر).")
                    print(f"[ERROR] اليوزرنيم غير صالح: {new_username}")
                except UsernameNotOccupiedError:
                    await event.reply("❌ اليوزرنيم المطلوب غير متاح أو مستخدم من قبل شخص آخر.")
                    print(f"[ERROR] اليوزرنيم مشغول: {new_username}")
                except FloodWaitError as e:
                    await event.reply(f"❌ حدث خطأ: عليك الانتظار {e.seconds} ثوانٍ قبل محاولة تغيير اليوزرنيم مرة أخرى.")
                    print(f"[ERROR] انتظار FloodWait: {e}")
                except Exception as e:
                    await event.reply(f"❌ حدث خطأ أثناء تغيير اليوزرنيم: `{e}`")
                    print(f"[ERROR] خطأ عام في تغيير اليوزرنيم: {e}")
            else:
                await event.reply("الرجاء تحديد يوزرنيم جديد بعد الأمر، مثال: `/change_username my_new_username`")

        elif command == '/join':
            if len(message_text.split(' ', 1)) > 1:
                target_entity = message_text.split(' ', 1)[1]
                try:
                    if 't.me/joinchat/' in target_entity or 't.me/+' in target_entity:
                        hash_part = target_entity.split('/')[-1]
                        await user_client(ImportChatInviteRequest(hash_part))
                        await event.reply(f"✅ تم الانضمام إلى المجموعة/القناة عبر رابط الدعوة بنجاح.")
                        print(f"[LOG] تم الانضمام عبر رابط دعوة: {target_entity}")
                    else:
                        await user_client(JoinChannelRequest(target_entity))
                        await event.reply(f"✅ تم الانضمام إلى: **{target_entity}** بنجاح.")
                        print(f"[LOG] تم الانضمام إلى: {target_entity}")
                except Exception as e:
                    await event.reply(f"❌ حدث خطأ أثناء الانضمام إلى {target_entity}: `{e}`")
                    print(f"[ERROR] خطأ في الانضمام: {e}")
            else:
                await event.reply("الرجاء تحديد يوزرنيم أو رابط دعوة بعد الأمر، مثال: `/join @telethon` أو `/join https://t.me/joinchat/ABCDEF...`")

        elif command == '/leave':
            if len(message_text.split(' ', 1)) > 1:
                target_entity = message_text.split(' ', 1)[1]
                try:
                    entity = await user_client.get_entity(target_entity)
                    await user_client(LeaveChannelRequest(entity))
                    await event.reply(f"✅ تم مغادرة: **{target_entity}** بنجاح.")
                    print(f"[LOG] تم مغادرة: {target_entity}")
                except Exception as e:
                    await event.reply(f"❌ حدث خطأ أثناء مغادرة {target_entity}: `{e}`")
                    print(f"[ERROR] خطأ في المغادرة: {e}")
            else:
                await event.reply("الرجاء تحديد يوزرنيم القناة أو المجموعة بعد الأمر، مثال: `/leave @telethon_discussions`")

        elif command == '/msg':
            parts = message_text.split(' ', 2)
            if len(parts) >= 3:
                target_username = parts[1]
                message_to_send = parts[2]
                try:
                    if not target_username.startswith('@'):
                        target_username = '@' + target_username
                    
                    await user_client.send_message(target_username, message_to_send)
                    await event.reply(f"✅ تم إرسال الرسالة إلى **{target_username}** بنجاح.")
                    print(f"[LOG] تم إرسال رسالة إلى {target_username}: {message_to_send}")
                except Exception as e:
                    await event.reply(f"❌ حدث خطأ أثناء إرسال الرسالة إلى {target_username}: `{e}`\n"
                                      "تأكد من صحة اليوزرنيم وأنك لم تحظر هذا المستخدم أو أنه قام بحظرك.")
                    print(f"[ERROR] خطأ في إرسال الرسالة: {e}")
            else:
                await event.reply("الرجاء تحديد اليوزرنيم والرسالة بعد الأمر، مثال: `/msg @username أهلاً بك!`")

        elif command == '/create_bot':
            if user_client: 
                is_creating_bot = True
                temp_event_to_reply = event 
                try:
                    bot_father_entity = await user_client.get_entity('BotFather')
                    await user_client.send_message(bot_father_entity, '/newbot')
                    await event.reply("✅ جاري بدء عملية إنشاء بوت جديد. **أرسل لي الآن اسم البوت الذي تريده:**")
                    print("[LOG] تم بدء عملية إنشاء بوت جديد.")
                except Exception as e:
                    is_creating_bot = False 
                    temp_event_to_reply = None
                    await event.reply(f"❌ حدث خطأ أثناء بدء عملية إنشاء البوت: `{e}`")
                    print(f"[ERROR] خطأ في بدء إنشاء البوت: {e}")
            else:
                await event.reply("❌ يجب أن يكون حسابك الشخصي متصلاً لبدء عملية إنشاء البوت.")

        elif command == '/create_channel':
            parts = message_text.split(' ', 2)
            if len(parts) >= 2:
                channel_name = parts[1]
                channel_about = parts[2] if len(parts) >= 3 else ''
                try:
                    result = await user_client(CreateChannelRequest(
                        title=channel_name,
                        about=channel_about,
                        megagroup=False 
                    ))
                    channel = result.chats[0]
                    
                    invite_link = None
                    try:
                        # جلب رابط الدعوة للقناة
                        invite_link = await user_client.get_channel_invite_link(channel)
                    except Exception as e:
                        print(f"[WARNING] لم يتمكن من الحصول على رابط دعوة للقناة: {e}")
                        invite_link = "لا يمكن الحصول على الرابط حالياً."

                    await event.reply(f"✅ تم إنشاء القناة **{channel_name}** بنجاح.\n"
                                      f"رابط الدعوة: `{invite_link}`")
                    print(f"[LOG] تم إنشاء قناة: {channel_name}, رابط الدعوة: {invite_link}")
                except Exception as e:
                    await event.reply(f"❌ حدث خطأ أثناء إنشاء القناة: `{e}`")
                    print(f"[ERROR] خطأ في إنشاء القناة: {e}")
            else:
                await event.reply("الرجاء تحديد اسم القناة بعد الأمر، مثال: `/create_channel قناتي_الجديدة هذا وصف القناة`")

        elif command == '/create_group':
            parts = message_text.split(' ', 1)
            if len(parts) >= 2:
                group_name = parts[1]
                
                try:
                    # إنشاء المجموعة بدون إضافة أعضاء
                    result = await user_client(CreateChannelRequest(
                        title=group_name,
                        megagroup=True, 
                        users=[] # لا تضف أي مستخدمين هنا
                    ))
                    group = result.chats[0]

                    invite_link = None
                    try:
                        invite_link = await user_client.get_chat_invite_link(group)
                    except Exception as e:
                        print(f"[WARNING] لم يتمكن من الحصول على رابط دعوة للمجموعة: {e}")
                        invite_link = "لا يمكن الحصول على الرابط حالياً."

                    await event.reply(f"✅ تم إنشاء المجموعة **{group_name}** بنجاح.\n"
                                      f"رابط الدعوة: `{invite_link}`")
                    print(f"[LOG] تم إنشاء مجموعة: {group_name}, رابط الدعوة: {invite_link}")
                except Exception as e:
                    await event.reply(f"❌ حدث خطأ أثناء إنشاء المجموعة: `{e}`")
                    print(f"[ERROR] خطأ في إنشاء المجموعة: {e}")
            else:
                await event.reply("الرجاء تحديد اسم المجموعة بعد الأمر، مثال: `/create_group كروبي_الجديد`")

        elif command == '/list_joined_chats':
            try:
                dialogs = await user_client.get_dialogs()
                joined_chats = []
                me_id = (await user_client.get_me()).id

                for d in dialogs:
                    if d.is_channel or d.is_group:
                        try:
                            # Skip private chats and bots
                            if d.is_user or d.id == me_id:
                                continue

                            # Get full chat details to check participation
                            full_chat = await user_client.get_entity(d.id)
                            
                            is_participant = False
                            # Check if the user is a participant (for channels and supergroups)
                            if isinstance(full_chat, Channel) and full_chat.left is False and full_chat.kicked is False:
                                is_participant = True
                            elif isinstance(full_chat, Chat) and full_chat.migrated_to_id is None: # Regular group (not migrated supergroup)
                                # For regular groups, check if you're a member (not easy directly from Chat object)
                                # We'll assume if it's in dialogs and not a private chat, you're in it.
                                is_participant = True
                            
                            # For supergroups/channels, can fetch participants to confirm
                            if isinstance(full_chat, (Channel, Chat)) and full_chat.megagroup:
                                try:
                                    # Attempt to get participant info
                                    participant = await user_client.get_participants(full_chat, filter=ChannelParticipantsAdmins, search='', limit=1, user_ids=[me_id])
                                    if participant: # If user is an admin
                                        is_participant = True
                                    else: # Check if general participant (this is more complex to get directly)
                                        # Simpler approach: if it's in dialogs and not "left/kicked", assume joined
                                        pass
                                except Exception as e_part:
                                    print(f"[DEBUG] Failed to get participant for {d.title}: {e_part}")

                            if is_participant:
                                chat_type = "قناة" if d.is_channel else "مجموعة"
                                invite_link = "لا يوجد رابط مباشر"
                                if d.username:
                                    invite_link = f"https://t.me/{d.username}"
                                else:
                                    try:
                                        # Try to get chat invite link (for private groups/channels)
                                        if d.is_channel:
                                            invite_link = await user_client.get_channel_invite_link(d.entity)
                                        elif d.is_group: # For groups, get_chat_invite_link might work
                                            invite_link = await user_client.get_chat_invite_link(d.entity)
                                    except Exception:
                                        pass # Failed to get invite link

                                joined_chats.append(f"- **{chat_type}:** `{d.title}`\n  **الرابط/اليوزرنيم:** `{invite_link}`")
                        except Exception as e:
                            print(f"[WARNING] خطأ في جلب معلومات الدردشة {d.title}: {e}")
                
                if joined_chats:
                    response_message = "**القنوات والمجموعات التي انضممت إليها:**\n\n" + "\n".join(joined_chats)
                else:
                    response_message = "لم تنضم إلى أي قنوات أو مجموعات حتى الآن."
                await event.reply(response_message)
                print("[LOG] تم عرض قائمة القنوات والمجموعات المنضم إليها.")
            except Exception as e:
                await event.reply(f"❌ حدث خطأ أثناء جلب القنوات والمجموعات المنضم إليها: `{e}`")
                print(f"[ERROR] خطأ في جلب القنوات والمجموعات المنضم إليها: {e}")


        elif command == '/list_my_managed_chats':
            try:
                dialogs = await user_client.get_dialogs()
                managed_chats = []
                me_id = (await user_client.get_me()).id

                for d in dialogs:
                    if d.is_channel or d.is_group:
                        try:
                            # Skip private chats and bots
                            if d.is_user or d.id == me_id:
                                continue

                            full_chat = await user_client.get_entity(d.id)
                            
                            is_manager = False
                            # Check if the user is the creator
                            if isinstance(full_chat, Channel) and full_chat.creator:
                                is_manager = True
                            elif isinstance(full_chat, Chat) and hasattr(full_chat, 'creator') and full_chat.creator:
                                is_manager = True
                            
                            # If not creator, check admin rights
                            if not is_manager:
                                try:
                                    # For channels and supergroups, check admin rights directly
                                    if isinstance(full_chat, Channel):
                                        participant = await user_client.get_participants(full_chat, filter=ChannelParticipantsAdmins, search='', limit=1, user_ids=[me_id])
                                        if participant and participant[0].admin_rights:
                                            is_manager = True
                                    # For regular groups, check if user is a 'chat creator' or 'chat admin'
                                    elif isinstance(full_chat, Chat):
                                        # Telethon's get_participants for Chat type might not directly give admin_rights for all members
                                        # We rely on the initial 'creator' check for Chat objects, or if it's migrated to supergroup
                                        pass # If it's a regular group, we're relying on 'creator' field.
                                except Exception as e_admin_check:
                                    print(f"[DEBUG] Error checking admin rights for {d.title}: {e_admin_check}")


                            if is_manager:
                                chat_type = "قناة" if d.is_channel else "مجموعة"
                                invite_link = "لا يوجد رابط مباشر"
                                if d.username:
                                    invite_link = f"https://t.me/{d.username}"
                                else:
                                    try:
                                        if d.is_channel:
                                            invite_link = await user_client.get_channel_invite_link(d.entity)
                                        elif d.is_group:
                                            invite_link = await user_client.get_chat_invite_link(d.entity)
                                    except Exception:
                                        pass
                                
                                managed_chats.append(f"- **{chat_type}:** `{d.title}`\n  **الرابط/اليوزرنيم:** `{invite_link}`")
                        except Exception as e:
                            print(f"[WARNING] خطأ في جلب معلومات الدردشة {d.title} لتحديد الإدارة: {e}")
                
                if managed_chats:
                    response_message = "**القنوات والمجموعات التي تديرها أو تملكها:**\n\n" + "\n".join(managed_chats)
                else:
                    response_message = "لا تدير أو تملك أي قنوات أو مجموعات حالياً."
                await event.reply(response_message)
                print("[LOG] تم عرض قائمة القنوات والمجموعات التي تديرها/تملكها.")
            except Exception as e:
                await event.reply(f"❌ حدث خطأ أثناء جلب القنوات والمجموعات التي تديرها: `{e}`")
                print(f"[ERROR] خطأ في جلب القنوات والمجموعات التي تديرها: {e}")

        elif command == '/list_sessions':
            try:
                authorizations = await user_client(GetAuthorizationsRequest())
                if authorizations.authorizations:
                    session_list = "**جلسات تسجيل الدخول النشطة:**\n"
                    for i, auth in enumerate(authorizations.authorizations):
                        current_session = " (هذه الجلسة)" if auth.current else ""
                        session_list += (
                            f"{i+1}. **الجهاز:** `{auth.device_model}`\n"
                            f"   **النظام:** `{auth.platform}`\n"
                            f"   **الدولة:** `{auth.country}`\n"
                            f"   **آخر استخدام:** `{auth.date_active.strftime('%Y-%m-%d %H:%M:%S')}`\n"
                            f"   **الـ Hash:** `{auth.hash}` {current_session}\n"
                            "--------------------\n"
                        )
                    await event.reply(session_list)
                    await event.reply("لاستبعاد جلسة، استخدم `/remove_session <الرقم>`.")
                else:
                    await event.reply("لا توجد جلسات تسجيل دخول نشطة.")
                print("[LOG] تم عرض قائمة الجلسات.")
            except Exception as e:
                await event.reply(f"❌ حدث خطأ أثناء جلب الجلسات: `{e}`")
                print(f"[ERROR] خطأ في جلب الجلسات: {e}")

        elif command == '/remove_session':
            if len(message_text.split(' ', 1)) > 1:
                try:
                    session_index = int(message_text.split(' ', 1)[1]) - 1
                    authorizations = await user_client(GetAuthorizationsRequest())
                    
                    if 0 <= session_index < len(authorizations.authorizations):
                        auth_to_remove = authorizations.authorizations[session_index]
                        
                        if auth_to_remove.current:
                            await event.reply("⚠️ لا يمكنك إزالة الجلسة الحالية التي تستخدمها للتحكم بالبوت!")
                            print("[WARNING] محاولة إزالة الجلسة الحالية.")
                            return

                        await user_client(ResetAuthorizationRequest(hash=auth_to_remove.hash))
                        await event.reply(f"✅ تم إزالة الجلسة رقم **{session_index + 1}** بنجاح.")
                        print(f"[LOG] تم إزالة الجلسة بالـ hash: {auth_to_remove.hash}")
                    else:
                        await event.reply("❌ رقم الجلسة غير صحيح. الرجاء استخدام رقم من قائمة `/list_sessions`.")
                except ValueError:
                    await event.reply("❌ الرجاء إدخال رقم صحيح للجلسة.")
                except Exception as e:
                    await event.reply(f"❌ حدث خطأ أثناء إزالة الجلسة: `{e}`")
                    print(f"[ERROR] خطأ في إزالة الجلسة: {e}")
            else:
                await event.reply("الرجاء تحديد رقم الجلسة المراد إزالتها، مثال: `/remove_session 1`")

        elif command == '/ping':
            try:
                await event.reply("✅ البوت متصل.")
                if user_client and user_client.is_connected():
                    me_user = await user_client.get_me()
                    await event.reply(f"✅ الحساب الشخصي ({utils.get_display_name(me_user)}) متصل.")
                else:
                    await event.reply("❌ الحساب الشخصي غير متصل. الرجاء إرسال StringSession مرة أخرى.")
                print("[LOG] تم الرد على أمر ping.")
            except Exception as e:
                await event.reply(f"❌ حدث خطأ أثناء التحقق من الاتصال: `{e}`")

        elif command == '/stop':
            await event.reply("👋 جاري إيقاف البوت والحساب...")
            print("[LOG] أمر إيقاف البوت تلقى. جاري الفصل...")
            if user_client and user_client.is_connected():
                await user_client.disconnect()
                print("[LOG] تم فصل الحساب الشخصي بنجاح.")
            await bot_client.disconnect()
            print("[LOG] تم فصل البوت بنجاح. يمكنك الآن إغلاق النافذة.")
            asyncio.get_event_loop().stop()
        
        else:
            await event.reply("أمر غير معروف أو غير صحيح. اكتب `/help` لعرض الأوامر المتاحة.")

    else:
        if command not in ['/start', '/session', '/help', '/ping', '/stop']:
            await event.reply("حسابك الشخصي غير متصل بعد. الرجاء إرسال StringSession باستخدام الأمر `/session <StringSession>`.")


async def main_run():
    print("جاري تشغيل بوت التحكم...")
    print(f"ابحث عن البوت في تليجرام باستخدام التوكن {bot_token} (أو استخدم اسم المستخدم الذي اخترته).")
    print(f"الـ ID الخاص بك هو: {your_user_id}. تأكد من صحته.")
    
    await bot_client.start(bot_token=bot_token)
    await bot_client.run_until_disconnected()

if __name__ == '__main__':
    print("جاري تشغيل بوت التحكم...")
    print(f"ابحث عن البوت في تليجرام باستخدام التوكن {bot_token} (أو استخدم اسم المستخدم الذي اخترته).")
    print(f"الـ ID الخاص بك هو: {your_user_id}. تأكد من صحته.")

    try:
        bot_client.start(bot_token=bot_token)
        bot_client.run_until_disconnected()
    except KeyboardInterrupt:
        print("\n[LOG] تم إيقاف البوت يدوياً (Ctrl+C).")
    except Exception as e:
        print(f"[CRITICAL ERROR] حدث خطأ غير متوقع: {e}")

