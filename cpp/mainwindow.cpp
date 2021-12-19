#include "mainwindow.h"
#include "./ui_mainwindow.h"

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::MainWindow)
{
    ui->setupUi(this);
    //ui->tabWidget->addTab(new capture_dialog(), "Capture");
    //ui->tabWidget->addTab(new QWidget(), "Configuration");

}

MainWindow::~MainWindow()
{
    delete ui;
}


void MainWindow::on_pushButton_clicked()
{
     //ui->listWidget->addItem("Netgear");
    //ui->tableWidget->row
    QTableWidgetItem *trow = new QTableWidgetItem("Tplink");
    ui->tableWidget->row(trow);
}


void MainWindow::on_toolButton_clicked()
{
    ui->label->setText("scan");
}


void MainWindow::on_tableWidget_itemSelectionChanged()
{

}

