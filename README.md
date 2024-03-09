# Índice

1. [Descripción del problema](#descripción-del-problema)
2. [Parte 1 - Ejecución directa](#parte-1---ejecución-directa)
3. [Parte 2 - Aplicación en un contenedor](#parte-2---aplicación-en-un-contenedor)
4. [Parte 3 - Docker compose](#parte-3---docker-compose)
5. [Parte 4 - Kubernetes](#parte-4---kubernetes)

## Descripción del problema

El problema plantea la creación de un servicio web utilizando Flask en Python, que integre datos de las APIs de OpenData Euskadi y AEMET. El servicio web debe ofrecer tres endpoints:

1. **GET /test**: Devuelve un mensaje de "OK" si el servidor está operativo.
2. **GET /trafico/{autopista}**: Devuelve el último parte de incidencias de tráfico en la autopista seleccionada.
3. **GET /tiempo/{ciudad}**: Devuelve la última predicción de temperaturas máximas y mínimas para la ciudad seleccionada.

Se deben tener en cuenta consideraciones importantes como el uso de servidores recomendados para producción, manejo de claves de API, formato JSON en respuestas, entre otros.

## Parte 1 - Ejecución directa

En esta parte se realiza la implementación y pruebas del servicio web utilizando Flask. Se deben realizar todas las pruebas sin utilizar contenedores.

## Parte 2 - Aplicación en un contenedor

Construcción de una imagen de contenedor que permita la ejecución del servicio web. Se debe proporcionar un Dockerfile para la construcción de la imagen y luego ejecutar el contenedor utilizando el comando `docker run`.

## Parte 3 - Docker compose

Preparación de la aplicación para funcionar con Docker Compose. Se deben ofrecer los servicios `/test`, `/trafico` y `/tiempo` en contenedores separados, permitiendo su escalabilidad. Además, se debe incluir un balanceador de carga basado en un contenedor nginx.

## Parte 4 - Kubernetes

Implementación del servicio de API utilizando un clúster Kubernetes. Se debe proporcionar un documento .yaml unificado para la configuración. Se plantean dos versiones: servidores idénticos y servidores especializados. En ambos casos se debe considerar el uso de un balanceador de carga o un recurso ingress según sea necesario.

Se puede considerar una mejora adicional donde se incluya un servicio accesible a través de `/test` que compruebe que el resto de los servicios están en marcha con al menos una instancia.
https://kubernetes.io/docs/tasks/access-application-cluster/ingress-minikube/

### Implementación en servidor cloud

Para ejecutar la aplicación en un servidor cloud se ha usado 
