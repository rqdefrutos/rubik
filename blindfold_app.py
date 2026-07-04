import rubik_new

print('Welcome to Blindfold App. Type a scramble and the sequence of letters that you need to memorize will show up. Type "random" to randomly generate a scramble. Type "exit" to exit the app.')
while True:
    x = input('\nInput: ')
    match x:
        case 'random':
            rubik_new.print_blindfold_sequence(rubik_new.random_sequence())
        case 'exit':
            break
        case _:
            try:
                rubik_new.print_blindfold_sequence(rubik_new.Algorithm(x))
            except:
                print('Something went wrong. Try again')