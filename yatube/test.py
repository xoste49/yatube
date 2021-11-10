from django.shortcuts import redirect


def user_contact(request):
    # проверим, пришёл ли к нам POST-запрос или какой-то другой:
    if request.method == 'POST':
        # создаём объект формы класса ContactForm и передаём в него полученные данные
        form = ContactForm(request.POST)

        # если все данные формы валидны - работаем с "очищенными данными" формы
        if form.is_valid():
            # берём валидированные данные формы из словаря form.cleaned_data
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['body']
            # при необходимости обрабатываем данные
            # ...
            # сохраняем объект в базу
            form.save()

            # Функция redirect перенаправляет пользователя 
            # на другую страницу сайта, чтобы защититься 
            # от повторного заполнения формы
            return redirect('/thank-you/')

        # если условие if form.is_valid() ложно и данные не прошли валидацию - 
        # передадим полученный объект в шаблон
        # чтобы показать пользователю информацию об ошибке

        # заодно заполним прошедшими валидацию данными все поля, 
        # чтобы не заставлять пользователя вносить их повторно
        return render(request, 'contact.html', {'form': form})

    # если пришёл не POST-запрос - создаём и передаём в шаблон пустую форму
    # пусть пользователь напишет что-нибудь
    form = ContactForm()
    return render(request, 'contact.html', {'form': form})