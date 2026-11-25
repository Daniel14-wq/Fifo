
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_fifo_8bits(dut):

    dut._log.info("INICIANDO PRUEBA FIFO 4x8")

    # CONFIGURACION INICIAL
    dut.ena.value = 1
    dut.clk.value = 0
    dut.rst_n.value = 0
    dut.ui_in.value = 0
    dut.uio_in.value = 0

    # RELOJ DE 50 MHz
    # Periodo = 20 ns
    async def ciclo(dato=0, escribir=0, leer=0):

        dut.clk.value = 0
        dut.ui_in.value = dato

        # uio[0] = WRITE
        # uio[1] = READ
        dut.uio_in.value = escribir | (leer << 1)

        await Timer(10, unit="ns")

        dut.clk.value = 1
        await Timer(10, unit="ns")

    # VERIFICAR ESTADO DE LA FIFO
    def verificar(cantidad, valido, dato):

        salida = int(dut.uo_out.value)
        uio = int(dut.uio_out.value)

        full = (uio >> 2) & 1
        empty = (uio >> 3) & 1
        read_valid = (uio >> 4) & 1
        used = (uio >> 5) & 0x07

        assert used == cantidad, (
            f"Contador incorrecto: {used}"
        )

        assert full == (cantidad == 4), (
            "Error en FULL"
        )

        assert empty == (cantidad == 0), (
            "Error en EMPTY"
        )

        assert read_valid == valido, (
            "Error en READ_VALID"
        )

        assert salida == dato, (
            f"Esperado {dato}, recibido {salida}"
        )

    # PRUEBA 1: RESET
    await ciclo()
    verificar(0, 0, 0)

    assert int(dut.uio_oe.value) == 0xFC

    dut.rst_n.value = 1
    dut._log.info("RESET CORRECTO")

    # PRUEBA 2: ESCRIBIR 4 DATOS
    datos = [25, 100, 200, 255]

    for cantidad, dato in enumerate(datos, 1):

        await ciclo(dato=dato, escribir=1)

        verificar(cantidad, 0, 0)

        dut._log.info(
            f"ESCRITURA CORRECTA: {dato}"
        )

    # PRUEBA 3: FIFO LLENA
    await ciclo(dato=50, escribir=1)

    verificar(4, 0, 0)
    dut._log.info("FIFO LLENA CORRECTAMENTE")

    # PRUEBA 4: LEER LOS DATOS
    for indice, esperado in enumerate(datos):

        await ciclo(leer=1)

        verificar(
            3 - indice,
            1,
            esperado
        )

        dut._log.info(
            f"LECTURA CORRECTA: {esperado}"
        )

    # PRUEBA 5: LECTURA EN VACIO
    await ciclo(leer=1)

    verificar(0, 0, 255)

    dut._log.info(
        "FIFO VACIA CORRECTAMENTE"
    )

    dut._log.info(
        "TODAS LAS PRUEBAS PASARON"
    )
