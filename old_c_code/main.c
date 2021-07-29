/**
 * @file
 * main.c
 * @author 
 * Juan J. Rojas
 * @date 
 * 7 Aug 2018
 * @brief 
 * Main source file. Includes the main loop and the interruption service routine. 
 * @par Institution:
 * LaSEINE / CeNT. Kyushu Institute of Technology.
 * @par Mail:
 * juan.rojas@tec.ac.cr
 * @par Git repository:
 * https://bitbucket.org/juanjorojash/cell_charger_discharger
 */

#include "charger_discharger.h"

/**@brief <b> This is the main function of the program. It initializes the system in every reset and takes care of several tasks that are excecuted every second. </b>
*/

void main(void) /// This function performs the folowing tasks:                     
{       
    initialize(); /// <ul> <li> Call the #initialize function
    __delay_ms(10);
    while(1) /// <li> <b> The main loop repeats the following forever: </b> 
    {
        if (SECF) /// <ul> <li> Check the #SECF flag, if it is set, 1 second has passed since last execution, so the folowing task are executed:
        {     
            SECF = 0; /// <ol> <li> Clear the #SECF flag to restart the 1 second timer
            scaling(); /// <li> Scale the average measured values by calling the #scaling function 
            log_control(); /// <li> Print the log in the serial terminal by calling the #log_control function
            cc_cv_mode(vavg, cvref, cmode); /// <li> Check if the system shall change to CV mode by calling the #cc_cv_mode function
            state_machine(); /// <li> Call the #state_machine function
            temp_protection(); /// <li> Call the #temp_protection function </ol> </ul> </ul>
        }
	}
}

/**@brief <b> This is the interruption service function. It will interrupt the code whenever the Timer1 overflow (0.975625 milliseconds) or when any character is received from the serial terminal via UART. </b>
*/
void __interrupt() ISR(void) /// This function performs the folowing tasks: 
{
    char recep = 0;
    
    if(TMR1IF) /// <li> Check the @b Timer1 interrupt flag, if it is set, the folowing task are executed:
    {
        TMR1H = 0xE1; // TMR1 clock is Fosc/4= 8Mhz (Tick= 0.125us). TMR1IF is set when the 16-bit register overflows. 7805 x 0.125us = 0.975625 ms.
        TMR1L = 0x83;/// <ol> <li> Load the @b Timer1 16-bit register so it overflow every 0.975625 ms 
        TMR1IF = 0; /// <li> Clear the @b Timer1 interrupt flag
        v = read_ADC(V_CHAN); /// <li> Read the ADC channel #V_CHAN and store the value in #v. Using the #read_ADC() function
        i = read_ADC(I_CHAN); /// <li> Read the ADC channel #I_CHAN and store the value in #i. Using the #read_ADC() function
        i = (uint16_t) (abs ( 2048 - (int)i ) ); /// <li> Substract the 2.5V bias from #i, store the absolute value in #i   
        t = read_ADC(T_CHAN); /// <li> Read the ADC channel #T_CHAN and store the value in #t. Using the #read_ADC() function 
        if (conv) control_loop(); /// <li> Call the #control_loop() function
        calculate_avg(); /// <li> Call the #calculate_avg() function
        timing(); /// <li> Call the #timing() function
        if (TMR1IF) UART_send_string((char*)"TIMING_ERROR"); /// <li> If the @b Timer1 interrupt flag is set, there is a timing error, print "TIMING_ERROR" into the terminal. </ol>
    }

    if(RCIF)/// <li> Check the @b UART reception interrupt flag, if it is set, the folowing task are executed:
    {
        if(RC1STAbits.OERR) /// <ol> <li> Check for any errors and clear them
        {
            RC1STAbits.CREN = 0;  
            RC1STAbits.CREN = 1; 
        }
        while(RCIF) recep = RC1REG; /// <li> Store the received character
        switch (recep)
        {
        case 0x63: /// <li> If a @b "c" was received, the process shall stop, then:
            STOP_CONVERTER(); /// - Stop the converter by calling the #STOP_CONVERTER() macro
            state = STANDBY; /// - Go to #STANDBY state
            break;
        case 0x6E: /// <li> If @p an @b "n" was received, the system shall jump to the next cell, then:
            STOP_CONVERTER(); /// - Stop the converter by calling the #STOP_CONVERTER() macro
            state = ISDONE; /// - Go to #ISDONE state
            break;
        default: /// <li> In any other case, do nothing
            recep = 0; 
        } /// </ol> </ul>
    }  
}