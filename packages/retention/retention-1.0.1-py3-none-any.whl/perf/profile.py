"""Simple profile script for power_retention components - just runs the function once for Nsight Compute profiling"""
import torch
import argparse
from retention.create_inputs import create_inputs
from retention.vidrial_fused import power_retention as power_retention_vidrial_fused
from retention._query_state.vidrial_fused import query_state as query_state_vidrial_fused
from retention._update_state.vidrial_fused import update_state as update_state_vidrial_fused
from retention._attention import attention_triton
from retention._query_state.create_inputs import create_inputs as create_inputs_query_state
from retention._update_state.create_inputs import create_inputs as create_inputs_update_state
from retention._attention.create_inputs import create_inputs as create_inputs_attention
from vidrial.jit.decorator import set_settings, PickBest, PickAny

import logging

logging.basicConfig(level=logging.DEBUG)



def str_to_dtype(s: str):
    """Convert string to torch dtype."""
    if s == 'float16':
        return torch.float16
    elif s == 'float32':
        return torch.float32
    elif s == 'bfloat16':
        return torch.bfloat16
    else:
        raise ValueError(f"Invalid dtype: {s}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Simple Power Full Profile Script for Nsight Compute")
    
    # Component and mode arguments (required)
    parser.add_argument('component', choices=['power_retention', 'query_state', 'update_state', 'attention'],
                       help='Component to profile')
    parser.add_argument('mode', choices=['fwd', 'bwd', 'fwd+bwd'],
                       help='Execution mode: forward, backward, or both')
    
    # Configuration arguments
    parser.add_argument('--b', type=int, default=1, help='Batch size (default: 1)')
    parser.add_argument('--t', type=int, default=65536, help='Sequence length (default: 65536)')
    parser.add_argument('--h', type=int, default=8, help='Number of heads (default: 8)')
    parser.add_argument('--d', type=int, default=64, help='Head dimension (default: 64)')
    parser.add_argument('--dtype', type=str, default='bfloat16', 
                       choices=['float16', 'float32', 'bfloat16'],
                       help='Data type (default: bfloat16)')
    parser.add_argument('--deg', type=int, default=2, help='Degree (default: 2)')
    parser.add_argument('--chunk-size', type=int, default=1024, help='Chunk size (default: 1024)')
    parser.add_argument('--no-compile', action='store_true', help='Disable torch.compile')
    parser.add_argument('--no-gating', action='store_true', help='Disable gating')
    
    args = parser.parse_args()
    
    # Check if d=128 is supported (it's not in power_retention yet)
    if args.d == 128 and args.component == 'power_retention':
        raise ValueError("d=128 is not supported by power_retention yet")
    
    # Create inputs based on component
    if args.component == 'power_retention':
        inputs = create_inputs(
            b=args.b,
            t=args.t,
            h=args.h,
            d=args.d,
            dtype=str_to_dtype(args.dtype),
            device='cuda',
            deg=args.deg,
            chunk_size=args.chunk_size,
            gating=not args.no_gating,
            requires_grad='bwd' in args.mode,
        )
        fn = power_retention_vidrial_fused
        
    elif args.component == 'query_state':
        # For query_state, we need to use chunk_size as the sequence length
        inputs = create_inputs_query_state(
            b=args.b,
            n=args.t // args.chunk_size,  # number of chunks
            c=args.chunk_size,  # chunk size
            h=args.h,
            d=args.d,
            dtype=str_to_dtype(args.dtype),
            device='cuda',
            deg=args.deg,
            requires_grad='bwd' in args.mode,
            use_vidrial_layout=True,  # Required for vidrial
            fused_norm=True,  # Required for fused version
        )
        fn = query_state_vidrial_fused
        
    elif args.component == 'update_state':
        # For update_state, we need to use chunk_size as the sequence length
        inputs = create_inputs_update_state(
            b=args.b,
            n=args.t // args.chunk_size,  # number of chunks
            c=args.chunk_size,  # chunk size
            h=args.h,
            d=args.d,
            deg=args.deg,
            dtype=str_to_dtype(args.dtype),
            device='cuda',
            requires_grad='bwd' in args.mode,
            use_vidrial_layout=True,  # Required for vidrial
        )
        fn = update_state_vidrial_fused
        
    elif args.component == 'attention':
        inputs = create_inputs_attention(
            b=args.b,
            t=args.t,
            h=args.h,
            d=args.d,
            dtype=str_to_dtype(args.dtype),
            device='cuda',
            deg=args.deg,
            gating=not args.no_gating,
            requires_grad='bwd' in args.mode,
        )
        fn = attention_triton  # Keep attention_triton since there's no vidrial version
    
    # Compile if requested
    if not args.no_compile:
        fn_compiled = torch.compile(fn)
    else:
        fn_compiled = fn
    
    print(f"Running {args.component} with {args.mode} mode")
    print(f"Configuration: b={args.b}, t={args.t}, h={args.h}, d={args.d}, "
          f"dtype={args.dtype}, deg={args.deg}, chunk_size={args.chunk_size}, "
          f"compile={not args.no_compile}")
    
    # Run the kernel once
    if args.mode == 'fwd':
        outputs = fn_compiled(**inputs)
        print(f"Forward pass completed. Output shape: {outputs.shape}")
        
    elif args.mode == 'bwd':
        outputs = fn_compiled(**inputs)
        # Handle functions that return tuples (like update_state)
        if isinstance(outputs, tuple):
            grads = tuple(torch.ones_like(out) for out in outputs)
        else:
            grads = torch.ones_like(outputs)
        torch.autograd.backward(outputs, grad_tensors=grads)
        print(f"Backward pass completed")
        
    elif args.mode == 'fwd+bwd':
        outputs = fn_compiled(**inputs)
        # Handle functions that return tuples (like update_state)
        if isinstance(outputs, tuple):
            grads = tuple(torch.ones_like(out) for out in outputs)
        else:
            grads = torch.ones_like(outputs)
        torch.autograd.backward(outputs, grad_tensors=grads)
        print(f"Forward + backward pass completed. Output shape: {outputs.shape}")


if __name__ == '__main__':
    with set_settings(policy=PickBest):
        main()
