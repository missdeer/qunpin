#-------------------------------------------------
#
# Project created by QtCreator 2012-10-16T15:17:23
#
#-------------------------------------------------

QT       += core

QT       -= gui

TARGET = epub
CONFIG   += console
CONFIG   -= app_bundle

TEMPLATE = app


SOURCES += main.cpp

win32:CONFIG(release, debug|release): LIBS += -L$$OUT_PWD/../../../3rd-party/quazip/release/ -lquazip
else:win32:CONFIG(debug, debug|release): LIBS += -L$$OUT_PWD/../../../3rd-party/quazip/debug/ -lquazip
else:unix:!symbian: LIBS += -L$$OUT_PWD/../../../3rd-party/quazip/ -lquazip

INCLUDEPATH += $$PWD/../../../3rd-party/quazip
DEPENDPATH += $$PWD/../../../3rd-party/quazip
