from kivy.uix.popup import Popup
from kivy.uix.label import Label


class error_b(Exception):
    "El calculo de b dio negativo"
    pass
class error_sID(Exception):
    "Se cargo una FCE desconocida"
    pass
class error_fnID(Exception):
    "Se cargo una Fn desconocida"
    pass
class error_pID(Exception):
    "Se cargo un producto desconocido"
    pass


popup_error_sID = Popup(title='Error al ingresar los datos',
content=Label(text='Has introducido una FCE desconocida'),
size_hint=(None, None), size=(600, 400))

popup_error_fnID = Popup(title='Error al ingresar los datos',
content=Label(text='Has introducido una Fn desconocida'),
size_hint=(None, None), size=(600, 400))

popup_error_pID = Popup(title='Error al ingresar los datos',
content=Label(text='Has introducido un producto desconocido'),
size_hint=(None, None), size=(600, 400))

popup_carga_incorrecta_de_datos = Popup(title='Error al ingresar los datos',
content=Label(text='Has introducido un caracter incorrecto. Utiliza solo letras o numeros'),
size_hint=(None, None), size=(600, 400))

popup_export_excel_abierto = Popup(title='Error al intentar exportar los datos',
content=Label(text='Nombre incorrecto de archivo.\nAsegurese que no exista otro archivo abierto con el mismo nombre.\n\nModifique el nombre o cierre el archivo\n\nPulse fuera del recuadro para continuar'),
size_hint=(None, None), size=(600, 400))

popup_b_negativo = Popup(title='Error al calcular el b',
content=Label(text='Verifique los datos ingresados'),
size_hint=(None, None), size=(600, 400))