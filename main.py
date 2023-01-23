import equations
import errors as e
#import openpyxl
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd



class objeto(object):   # Utilizo este objeto para almacenar los inputs de la interfase y pasarlo a las funciones necesarias
    pass


class FirstWindow(Screen):
    # por alguna razon no se pueden iniciar variables con mayusculas en el my.kv
    umax = ObjectProperty(None)
    yxs = ObjectProperty(None)
    tf = ObjectProperty(None)       
    fce = ObjectProperty(None)
    id_fce = ObjectProperty(None)
    fn = ObjectProperty(None)
    id_fn = ObjectProperty(None)
    x0 = ObjectProperty(None)
    kLa = ObjectProperty(None)

    def TakeInputs(self):   #Este metodo toma los datos de los campos 
        p=objeto()      # Aqui almacenare los inputs

        p.umax = float(self.umax.text)
        p.yxs = float(self.yxs.text)
        p.tf = float(self.tf.text)
        p.fce = float(self.fce.text)
        p.id_fce = self.id_fce.text
        p.fn = float(self.fn.text)
        p.id_fn = self.id_fn.text
        p.x0 = float(self.x0.text)
        p.yps = float(self.yps.text)
        p.id_p = self.id_p.text
        p.kLa = float(self.kLa.text)
        
# Inputs de la ventada avanzados
        p.ms = float(self.manager.ids.secondw.ms.text)
        p.tLag = float(self.manager.ids.secondw.tLag.text)
        p.pp_O2 = float(self.manager.ids.secondw.pp_O2.text)
        p.beta = float(self.manager.ids.secondw.beta.text)

            
        return p


    def CreateDataset(self):


        try:
            df = equations.GenerarCineticaBatch(FirstWindow.TakeInputs(self))
            
            name_file = self.excel.text + ".xlsx"
            round(df[["X", "S", "N"]],3).to_excel("../"+name_file)
        except e.error_b:
            e.popup_b_negativo.open()
        except e.error_sID:
            e.popup_error_sID.open()
        except e.error_fnID:
            e.popup_error_fnID.open()
        except e.error_pID:
             e.popup_error_pID.open()   
        except PermissionError:
            e.popup_export_excel_abierto.open()
            
        except :
        
            e.popup_carga_incorrecta_de_datos.open()

        
        
    def graficar(self):
#   https://pandas.pydata.org/pandas-docs/version/0.23/generated/pandas.DataFrame.plot.html
#   Este link tiene la documentacion con parametros de matplotlib + pandas
        try:
            df = equations.GenerarCineticaBatch(FirstWindow.TakeInputs(self))
            
            df["P"] = np.where(df["P"] == 0, np.nan, df["P"])

            df[["X", "S", "N", "P"]].plot()
            plt.show()

        except e.error_b:
            e.popup_b_negativo.open()
        except e.error_sID:
            e.popup_error_sID.open()
        except e.error_fnID:
            e.popup_error_fnID.open()
        except e.error_pID:
             e.popup_error_pID.open()
             
        except:
             e.popup_carga_incorrecta_de_datos.open()


class SecondWindow(Screen):
    pass
    
        
class ContinuousWindow(Screen):
    
    def GetInputsContinuo(self):
        fs = self.manager.get_screen("Pantalla Principal")  # Obtengo la pantalla y la guardo en una variable, para luego llamar funciones de dicha pantalla
        p = fs.TakeInputs() # Colecto valores de todos los Text Inputs
        
        p.d = float(self.d.text)
        p.sr_c = float(self.sr_c.text)
        p.nr_c = float(self.nr_c.text)
        return p
        
    def GenerarEstadoEstacionario(self, graph=True):
        p = ContinuousWindow.GetInputsContinuo(self)
        df = equations.GenerarContinuo(p)
        if graph:
            df.plot()
            plt.show()
        return df
        
    def BarridoDe_D(self, graph=True):
        p = ContinuousWindow.GetInputsContinuo(self)
        
        rangoD = float(self.barrido1.text), float(self.barrido2.text), float(self.barrido3.text)
        df = equations.BarridoDe_D(p, rangoD)
        if graph:
            df.plot()
            plt.show()
        return df

        
    def CreateDataset_ee(self):
        try:
            df = ContinuousWindow.GenerarEstadoEstacionario(self, graph=False)
            
            name_file = self.excel_ee.text + ".xlsx"
            round(df[["X", "S", "N"]],3).to_excel("../"+name_file)
        except e.error_b:
            e.popup_b_negativo.open()
        except e.error_sID:
            e.popup_error_sID.open()
        except e.error_fnID:
            e.popup_error_fnID.open()
        except e.error_pID:
             e.popup_error_pID.open()   
        except PermissionError:
            e.popup_export_excel_abierto.open()
            
        except :
        
            e.popup_carga_incorrecta_de_datos.open()
        
    def CreateDataset_bd(self):
        try:
            df = ContinuousWindow.BarridoDe_D(self, graph=False)
            
            name_file = self.excel_bd.text + ".xlsx"
            round(df[["X", "S", "N"]],3).to_excel("../"+name_file)
        except e.error_b:
            e.popup_b_negativo.open()
        except e.error_sID:
            e.popup_error_sID.open()
        except e.error_fnID:
            e.popup_error_fnID.open()
        except e.error_pID:
             e.popup_error_pID.open()   
        except PermissionError:
            e.popup_export_excel_abierto.open()
            
        except :
        
            e.popup_carga_incorrecta_de_datos.open()
            
            
class FeedBatchWindow(Screen):
    def GenerarAlimentado(self, graph=True):
        fs = self.manager.get_screen("Pantalla Principal")  # Obtengo la pantalla y la guardo en una variable, para luego llamar funciones de dicha pantalla
        p = fs.TakeInputs() # Colecto valores de todos los Text Inputs
        
        p.f = float(self.f.text)
        p.uc = float(self.uc.text)
        p.t = float(self.t_a.text)
        p.v = float(self.v.text)
        p.sr_a = float(self.sr_a.text)
        p.nr_a = float(self.nr_a.text)
    
        df = equations.GenerarAlimentado(p)
        if graph:
            df[["X", "S", "N"]].plot()
            plt.show()
        return df
        
        
        
    def CreateDataset_ba(self, graph=False):
        try:
            df = FeedBatchWindow.GenerarAlimentado(self, graph=False)
            
            name_file = self.excel_ba.text + ".xlsx"
            round(df[["X", "S", "N"]],3).to_excel("../"+name_file)
        except e.error_b:
            e.popup_b_negativo.open()
        except e.error_sID:
            e.popup_error_sID.open()
        except e.error_fnID:
            e.popup_error_fnID.open()
        except e.error_pID:
             e.popup_error_pID.open()   
        except PermissionError:
            e.popup_export_excel_abierto.open()
            
        except :
        
            e.popup_carga_incorrecta_de_datos.open()
class WindowManager(ScreenManager):
    pass

kv = Builder.load_file("my.kv")



class myApp(App):
    def build(self):
        return kv

if __name__ == "__main__":
    myApp().run()
    
    #%matplotlib qt