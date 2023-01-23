# Microorganism_Grouth_Simulator
Una herramienta educativa para entender las matemáticas detrás del crecimiento de un microorganismo

Bienvenido a Microorganism_Grouth_Simulator v1.0

Este programa está diseñado para ser utilizado por cualquier estudiante que quiera interactuar con conceptos de un bioproceso clásico, de forma interactiva.

El simulador está estructurado en torno a una interfaz principal, donde se puede simular el crecimiento básico en un sistema de cultivo por lotes. En la pantalla puedes ver todos los parámetros de cultivo que puedes modificar. Una vez cargado, puede ver el crecimiento en un gráfico o descargar los datos para analizarlos con un programa externo.
![imagen](https://user-images.githubusercontent.com/71038398/214141009-9ef75461-75b5-4439-be4d-07dea2131b72.png)

Dentro de la interfaz principal, uno puede modificar parámetros específicos, en la pestaña "opciones avanzadas".
Además, es posible realizar otro tipo de cultivos: Cultivo continuo y Alimentación por lotes.

Para ambos casos, se simula el cultivo anterior utilizando los valores ingresados para el campo desde la pantalla principal.

Sin mucho más que explicar, puedes jugar con los parámetros y ver los resultados obtenidos. El simulador está diseñado para no fallar en un error de cálculo del cultivo, sino que generará lo que sucedería en la vida real. Por ejemplo: si se diseña un cultivo continuo, pero se establece una tasa de dilución más alta que el crecimiento del microorganismo, el cultivo continuo no ocurrirá y, en cambio, mostrará que el microorganismo se elimina por lavado, como lo haría en un reactor. verdadero. .

**Aclaraciones**

Esta versión 1.0 es la primera versión funcional, la interfaz gráfica es algo precaria al igual que las gráficas generadas con matplotlib. El objetivo es contar con una herramienta didáctica, que a futuro pueda ser mejorada para una mejor experiencia de usuario.

** Descargo de responsabilidad **

En ningún caso esta aplicación ha sido diseñada para realizar cálculos sobre un cultivo real. Si bien las matemáticas se ajustan a la realidad, los modelos matemáticos se limitan estrictamente a los conceptos que se imparten en la cátedra de Bioprocesos I de la Universidad Nacional de Quilmes. En caso de que quieras hacer un cálculo útil, existen modelos mejores y más sofisticados para aplicar.

# Microorganism_Grouth_Simulator
An educational tool for understanding the math behind a microorganism growth

Welcome to Microorganism_Grouth_Simulator v1.0

This program is designed to be used by any student who wants to interact with concepts of a classic bioprocess, in an interactive way.

The simulator is structured around a main interface, in which one can simulate basic growth in a batch culture system. On the screen you can see all the crop parameters that you can modify. Once loaded you can view the growth in a graph, or download the data to be analyzed with an external program.
![image](https://user-images.githubusercontent.com/71038398/214141009-9ef75461-75b5-4439-be4d-07dea2131b72.png)

Within the main interface, one can modify specific parameters, in the "advanced options" tab.
In addition, it is possible to carry out other types of cultures: Continuous culture and Batch fed.

For both cases, the previous crop is simulated using the values entered for the batch from the main screen.

Without much more to explain, one can play with the parameters and see the results obtained. The simulator is designed not to fail in the face of a bad crop calculation, but rather it will generate what would happen in real life. For example: If one designs a continuous culture, but sets a dilution rate higher than the growth of the microorganism, the continuous culture will not occur and will instead show how the microorganism is washed until it disappears, as it would in a real reactor. .

**Clarifications**

This version 1.0 is the first functional version, the graphical interface is somewhat precarious as are the graphs generated with matplotlib. The objective is to have a teaching tool, which in the future could be improved for a better user experience.

** Disclaimer **

Under no point of view this application was designed to perform calculations on a real crop. Although mathematics adjusts to reality, mathematical models are strictly limited to the concepts taught in the Bioprocesses I chair at the National University of Quilmes. In case you want to make a useful calculation, there are better and more sophisticated models to apply.
