from tkinter import *

root = Tk()
root.title('Monopoly Settings')
root.geometry('750x700+200+10')
root.configure(background='#808080')
font = 'bulbulpoly 3'
lines = open('settings.txt', 'r').readlines()


def replace_line(line_num, text, filepath):
    lines = open(filepath, 'r').readlines()
    lines[line_num] = str(text) + '\n'
    out = open(filepath, 'w')
    out.writelines(lines)
    out.close()


def save_data():
    global audio_path, fps, src_video_path, output_name, precision
    resolution = selected_language.get()
    fps = int(FPSEntry.get())

    replace_line(0, resolution, 'settings.txt')
    replace_line(1, fps, 'settings.txt')
    print('Значения строк сохранены')
    root.destroy()


selected_language = StringVar()

resolutions = [['1280x720', 1], ['1920x1080', 2]]

resolution_text = Label(text='Выберите разрешение экрана', font=(font, 25), background='#808080', foreground='black')
resolution_text.pack(anchor='nw', padx=10)

for i in resolutions:
    resolution_choice = Radiobutton(text=i[0], value=i[1], font=(font, 25), background='#808080', foreground='black', variable=selected_language)
    resolution_choice.pack(anchor='nw', padx=10)

FPSText = Label(text='Введите желаемый FPS', font=(font, 25), background='#808080', foreground='black')
FPSText.pack(anchor='nw', padx=10)

FPSEntry = Entry(background='gray', font=(font, 25), foreground='white', width=3)
FPSEntry.pack(anchor='nw', padx=10)
FPSEntry.insert(0, lines[1][:-1])

btn1 = Button(text='Сохранить', command=save_data, font=(font, 20))
btn1.pack(anchor='nw', padx=10, pady=10)

root.mainloop()