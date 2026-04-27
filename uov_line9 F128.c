/*
 * uov_line9.c  --  version sobre F_128
 *
 * Implementacion de la Linea 9 del algoritmo UOV.Sign:
 *     y = [v^T * P_i^(1) * v]_{i in [m]}
 *
 * Parametros del experimento:
 *     - Campo: F_128 = F_2[x] / (x^7 + x + 1)
 *       Los elementos se representan como enteros de 7 bits (0..127)
 *       almacenados en un uint8_t. El polinomio irreducible es 0x83.
 *     - n = 3 (longitud del vector vinegar v)
 *     - m = 3 (numero de matrices P_i, y por tanto longitud de y)
 *     - Las matrices P_i son triangulares superiores fijas con entradas
 *       en F_128.
 *
 * Los 10 vectores de perfilamiento se seleccionan mediante el #define
 * V_INDEX (valores 0..9). Cambiar el indice y recompilar para cada
 * ejecucion del perfilamiento.
 */

#include <stdint.h>
#include <stdio.h>

/* ========================================================================
 * SELECTOR DEL VECTOR DE ENTRADA -- cambiar antes de cada compilacion
 * Valores validos: 0, 1, 2, ..., 9
 * ======================================================================== */
#define V_INDEX 0
/* ======================================================================== */

#define N 3
#define M 3
#define F128_IRRED 0x83u   /* x^7 + x + 1 */
#define F128_MASK  0x7Fu   /* mascara de 7 bits */

/* ------------------------------------------------------------------------
 * Aritmetica en F_128
 * ------------------------------------------------------------------------ */

/* Suma en F_128: XOR bit a bit de dos elementos de 7 bits. */
static uint8_t f128_add(uint8_t a, uint8_t b)
{
    return (a ^ b) & F128_MASK;
}

/* Multiplicacion en F_128 por shift-and-xor con reduccion modulo
 * el polinomio irreducible x^7 + x + 1.
 *
 * Recorremos los 7 bits del multiplicador b, acumulando copias desplazadas
 * de a. Tras cada desplazamiento, si el bit 7 de a queda activo, se reduce
 * haciendo XOR con el irreducible (el bit 7 se cancela y se suma x+1).
 */
static uint8_t f128_mul(uint8_t a, uint8_t b)
{
    uint8_t result = 0;
    uint8_t aa = a & F128_MASK;
    uint8_t bb = b & F128_MASK;

    for (int i = 0; i < 7; i++) {
        if (bb & 1u) {
            result ^= aa;
        }
        bb >>= 1;

        /* Desplazar aa a la izquierda (multiplicar por x) */
        uint8_t carry = aa & 0x40u;   /* bit 6, el mas alto valido */
        aa = (aa << 1) & 0x7Fu;
        if (carry) {
            aa ^= (F128_IRRED & F128_MASK);  /* reducir: restar x^7, sumar x+1 */
        }
    }
    return result & F128_MASK;
}

/* ------------------------------------------------------------------------
 * Matrices P_i triangulares superiores 3x3 con entradas en F_128
 * Elegidas con valores diversos para generar patrones de multiplicacion
 * ricos durante el calculo.
 * ------------------------------------------------------------------------ */
static const uint8_t P1[N][N] = {
    { 0x23, 0x5A, 0x11 },
    { 0x00, 0x4F, 0x6C },
    { 0x00, 0x00, 0x37 }
};

static const uint8_t P2[N][N] = {
    { 0x71, 0x0D, 0x42 },
    { 0x00, 0x2E, 0x19 },
    { 0x00, 0x00, 0x5B }
};

static const uint8_t P3[N][N] = {
    { 0x08, 0x66, 0x3A },
    { 0x00, 0x74, 0x25 },
    { 0x00, 0x00, 0x1F }
};

/* ------------------------------------------------------------------------
 * Los 10 vectores v del banco de perfilamiento
 * ------------------------------------------------------------------------ */
static const uint8_t V_BANK[10][N] = {
    { 0x00, 0x00, 0x00 },   /* v_0: trivial */
    { 0x01, 0x00, 0x00 },   /* v_1: un solo bit */
    { 0x00, 0x7F, 0x00 },   /* v_2: maximo peso en el medio */
    { 0x7F, 0x7F, 0x7F },   /* v_3: todo a uno */
    { 0x2A, 0x55, 0x7F },   /* v_4: patron alternante */
    { 0x55, 0x2A, 0x55 },   /* v_5: alternante espejo */
    { 0x0F, 0x33, 0x55 },   /* v_6: pesos crecientes */
    { 0x11, 0x22, 0x44 },   /* v_7: un bit por byte, desplazado */
    { 0x7F, 0x00, 0x7F },   /* v_8: extremos */
    { 0x13, 0x57, 0x2B }    /* v_9: arbitrarios */
};

/* ------------------------------------------------------------------------
 * Forma cuadratica: y_i = v^T * P_i * v  en F_128
 * ------------------------------------------------------------------------ */
static uint8_t quadratic_form(const uint8_t v[N], const uint8_t P[N][N])
{
    uint8_t acc = 0;
    uint8_t term;
    uint8_t prod;

    for (int j = 0; j < N; j++) {
        for (int k = 0; k < N; k++) {
            prod = f128_mul(v[j], P[j][k]);
            term = f128_mul(prod, v[k]);
            acc = f128_add(acc, term);
        }
    }
    return acc;
}

/* Calcula el vector y completo */
static void compute_y(const uint8_t v[N], uint8_t y[M])
{
    y[0] = quadratic_form(v, P1);
    y[1] = quadratic_form(v, P2);
    y[2] = quadratic_form(v, P3);
}

int main(void)
{
    const uint8_t *v = V_BANK[V_INDEX];
    uint8_t y[M];

    /* --- Inicio de la region de interes para el osciloscopio --- */
    compute_y(v, y);
    /* --- Fin de la region de interes --- */

    printf("V_INDEX = %d\n", V_INDEX);
    printf("v = (0x%02X, 0x%02X, 0x%02X)\n", v[0], v[1], v[2]);
    printf("y = (0x%02X, 0x%02X, 0x%02X)\n", y[0], y[1], y[2]);

    return 0;
}
