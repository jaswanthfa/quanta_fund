
import { Button } from '../ui/button';
import usePortalContext from '@/context/PortalContext';
import { Manager } from '@/lib/contracts/base';
import { FundProfile } from '@/lib/contracts/fundProfile';

export default function header(){

  return (
    <>
     
        <div className="mt-[45px] flex w-full  flex-wrap text-[20px] sm:w-full  sm:flex-wrap sm:px-0 sm:text-[30px] md:mt-[0px]  ">
          <h1
            data-cik="0001067983"
            style={{ fontWeight: 'bold', color: '#21385F' }}
            className=" text-center sm:text-start"
          >
            
          </h1>
          <div className="mx-auto text-sm font-medium text-gray-500 sm:mx-0 sm:ml-auto sm:text-end ">
           
                <>
                  <div className="rounded-md border-2 border-[gray] p-2 px-[2em] font-bold shadow-xl">
                    
                  </div>
                </>
              
          </div>
        </div>
    
    </>
  );
}
